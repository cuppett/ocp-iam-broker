import unittest
import jsonpatch
import webhook


class TestWebhookCase(unittest.TestCase):

    def test_update_pod_spec(self):

        original = {
            'kind': 'Pod',
            'apiVersion': 'v1',
            'spec': {
                'containers': [{
                    'name': 'awscli',
                    'image': 'quay.io/cuppett/aws-cli',
                    'command': ['aws'],
                    'args': ['s3', 'ls'],
                    'resources': {},
                    'volumeMounts': [{
                        'name': 'default-token-6f5pr',
                        'mountPath': '/var/run/secrets/kubernetes.io/serviceaccount'
                    }],
                    'terminationMessagePath': '/dev/termination-log',
                    'terminationMessagePolicy': 'File',
                    'imagePullPolicy': 'Always',
                    'securityContext': {
                        'capabilities': {
                            'drop': ['MKNOD']
                        }
                    }
                }, {
                    'name': 'awscli2',
                    'image': 'quay.io/cuppett/aws-cli',
                    'command': ['aws'],
                    'args': ['s3', 'ls'],
                    'resources': {},
                    'volumeMounts': [{
                        'name': 'default-token-6f5pr',
                        'mountPath': '/var/run/secrets/kubernetes.io/serviceaccount'
                    }],
                    'terminationMessagePath': '/dev/termination-log',
                    'terminationMessagePolicy': 'File',
                    'imagePullPolicy': 'Always',
                    'securityContext': {
                        'capabilities': {
                            'drop': ['MKNOD']
                        }
                    }
                }],
                'restartPolicy': 'Always',
                'terminationGracePeriodSeconds': 30,
                'dnsPolicy': 'ClusterFirst',
                'serviceAccountName': 'default',
                'serviceAccount': 'default',
                'securityContext': {
                    'seLinuxOptions': {
                        'level': 's0:c23,c17'
                    }
                },
                'imagePullSecrets': [{
                    'name': 'default-dockercfg-mqnqw'
                }],
                'schedulerName': 'default-scheduler',
                'priority': 0,
            }
        }

        new = webhook._update_pod_spec(original, 'test_secret')
        patch = jsonpatch.JsonPatch.from_diff(original, new)
        string_patch = patch.to_string()
        self.assertNotEqual(string_patch, '[]')

        jsonpatch.apply_patch(original, patch, True)

        self.assertEqual(len(original['spec']['containers']), 3)
        self.assertEqual(original['spec']['containers'][2]['name'], 'ocp-broker-proxy')
        self.assertEqual(original['spec']['containers'][1]['name'], 'awscli2')
        self.assertNotIn('env', original['spec']['containers'][2])
        self.assertIsNotNone(original['spec']['containers'][0]['env'])
        self.assertIsNotNone(original['spec']['containers'][1]['env'])
        print(patch.to_string())


if __name__ == '__main__':
    unittest.main()
