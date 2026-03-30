class FakeS3Body:
    def __init__(self, data: str):
        self._data = data

    def read(self):
        return self._data.encode('utf-8')


class FakeS3Client:
    def __init__(self, fake_files: dict[str, str]):
        self.files = fake_files

    def list_objects_v2(self, Bucket: str, Prefix: str):
        contents = [{'Key': k} for k in self.files if k.startswith(Prefix)]
        return {'Contents': contents}

    def get_object(self, Bucket: str, Key: str):
        return {'Body': FakeS3Body(self.files[Key])}
