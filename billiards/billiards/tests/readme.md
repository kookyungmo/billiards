#How to run existing tests
It's no difference with running tests of other django applications.

```shell
ptyhon manage.py test billiards
```

or run tests with verbose output

```shell
ptyhon manage.py test billiards --verbosity=2
ptyhon manage.py test billiards --verbosity=3
```

#How to write test code
##How to generate test data
Django allows to load fixtures when initialing test database or pre-starting test cases.

Our project has a customized command '**dumptestdata**' to dump data from product database for testing purpose.

The main code of dumptestdata looks like below, query expected data from product database then dump them as file. Free generate more data for your new test cases.

```python
poolroomTestDataQuery = Poolroom.objects.filter(Q(id=137) | Q(id=148) | Q(id=14))
data = serializers.serialize("json", poolroomTestDataQuery, indent=4)
out = open("%s/fixtures/poolroom.json" %(self.apppath), "w")
out.write(data)
out.close()
```
How to run **dumptestdata** command
```shell
ptyhon manage.py dumptestdata
```
##How to write test code
There is no special for writing test cases of our project and using fixtures for preparing test data before running test cases. Please refer the [official documentation of django](https://docs.djangoproject.com/en/1.4/topics/testing/) for more detail.