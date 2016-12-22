# -*- coding: utf-8 -*-

from boto3.session import Session
import aws_config
import json


class AwsBackup(object):
    '''
    '''

    def __init__(self):
        self.session = Session(aws_access_key_id=aws_config.aws_access_key_id,
                               aws_secret_access_key=aws_config.aws_secret_access_key,
                               region_name=aws_config.region)

    def read_old_snapshot(self):
        '''
        Read snapshot list.
        '''
        with open(aws_config.snapshot_backup_list, 'r') as f:
            try:
                data = f.read()
                snapshot_list = json.loads(data) if data else []
                if not isinstance(snapshot_list,list):
                    raise Exception('File Data Error')
                return snapshot_list
            except Exception:
                raise Exception('Read File Error')

    def write_new_snapshot(self, new_snapshot_list):
        with open(aws_config.snapshot_backup_list, 'w') as f:
            try:
                f.write(json.dumps(new_snapshot_list))
            except Exception:
                raise Exception('Write Data Error')

    def backup_snapshot(self):
        client = self.session.client('ec2')
        response = client.create_snapshot(VolumeId=aws_config.volumeid, Description='AutoBackup')
        return response.get('SnapshotId', None)

    def remove_snapshot(self, snapshot_id):
        ec2 = self.session.resource('ec2')
        snapshot = ec2.Snapshot(snapshot_id)
        snapshot.delete()

    def run(self):
        snapshot_list = self.read_old_snapshot()
        snapshot_list.append(self.backup_snapshot())

        if len(snapshot_list) > 5:
            for i in range(len(snapshot_list) - 5):
                snapshot_id = snapshot_list.pop(0)
                self.remove_snapshot(snapshot_id)
        self.write_new_snapshot(snapshot_list)


if __name__ == '__main__':
    AwsBackup().run()
