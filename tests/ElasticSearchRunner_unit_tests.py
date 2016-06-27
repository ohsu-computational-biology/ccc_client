#!/usr/bin/env python

import unittest
import ccc_client

# basic unit tests of the ccc_client services.
# These should not depend on any of the services actually running.


class TestCccClient(unittest.TestCase):

    def test_index_names(self):
        ccc = ccc_client.ElasticSearchRunner()
        rp = ccc_client.ElasticSearchRunner.RowParser(
            fileHeader=None,
            siteId=self.getSiteId(),
            user=self.getUser(),
            projectCode=self.getProject(),
            domainName='resource',
            es=None,
            domainDescriptors=ccc.DomainDescriptors,
            isMock=True,
            skipDtsRegistration=True
        )

        # index names
        self.assertEqual(rp.getIndexNameForDomain('resource'), self.getProject().lower() + '-' + 'aggregated-resource')
        self.assertEqual(rp.getIndexNameForDomain('sample'), self.getProject().lower() + '-' + 'sample')
        self.assertEqual(rp.getIndexNameForDomain('specimen'), self.getProject().lower() + '-' + 'specimen')
        self.assertEqual(rp.getIndexNameForDomain('patient'), self.getProject().lower() + '-' + 'patient')

        # row keys
        rowMap = {
            'patient_id': 'PATIENT1',
            'specimen_id': 'specImen1',
            'sample_id': 'saMple1',
            'ccc_did': 'ccc_did'
        }
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'resource'), 'ccc_did')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'sample'), self.getProject().lower() + '-' + 'sample' + '-sample1')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'specimen'), self.getProject().lower() + '-' + 'specimen-specimen1')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'patient'), self.getProject().lower() + '-' + 'patient-patient1')

    def test_import(self):
        ccc = ccc_client.ElasticSearchRunner()
        ccc.es = self.MockEs()

        # test lack of errors
        fp = "mock/file.txt"
        rowMap = ccc.publish_resource(
            filePath=fp,
            siteId=self.getSiteId(),
            user=self.getUser(),
            projectCode=self.getProject(),
            workflowId=None,
            mimeType="application/text",
            domainName="resource",
            inheritFrom=None,
            properties={},
            isMock=True
        )
        self.assertEqual(rowMap["filepath"], fp)
        self.assertEqual(rowMap["mimetype"], "application/text")

        # test mock inheritance
        rowMap = ccc.publish_resource('mock/file.txt', self.getSiteId(), self.getUser(), self.getProject(), None, "application/text", 'resource', 'abc', [], True)
        self.assertEqual(rowMap["inherit1"], "a")
        self.assertEqual(rowMap["inherit2"], "b")

        # test inheritance from other domain
        rowMap = ccc.publish_resource('mock/file.txt', self.getSiteId(), self.getUser(), self.getProject(), None, "application/text", 'resource', None, [
            "patient_id:patient1"
        ], True)
        self.assertFalse("inherit1" in rowMap.keys())
        self.assertFalse("inherit2" in rowMap.keys())
        self.assertEqual(rowMap["patientField1"], "a")
        self.assertEqual(rowMap["patientField2"], "b")

    class MockEs(object):
        def search(self, index=None, doc_type=None, ignore_unavailable=True, allow_no_indices=True,body=None):
            if "bool" in body["query"].keys():
                # this is called when searching for specific CCC_DID
                return {
                    "hits": {
                        "hits": [{
                            "_source": {
                                "inherit1": "a",
                                "inherit2": "b"
                            }
                        }]
                    }
                }
            elif "query_string" in body["query"].keys():
                #called when searching by patient_id
                return {
                    "hits": {
                        "hits": [{
                             "_source": {
                                 "patientField1": "a",
                                 "patientField2": "b"
                             }
                         }]
                    }
                }

    def index(self):
        print('indexing!')

    def getSiteId(self):
        return 'testSite'

    def getProject(self):
        return 'testProject'

    def getUser(self):
        return 'me'

if __name__ == '__main__':
    unittest.main()
