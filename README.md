# CTSRunner
CtsRunner for CTS test

Simple usage:

```python
import CTSRunner
cts = CTSRunner.cts
cts.version
cts.root_path
cts.run("l packages")
```

```python
import CTSRunner
cts = CTSRunner.cts
cts.run("run cts --plan CTS -l debug")
cts.get_last_result()
cts.get_last_logs()
```

```python
import CTSRunner
cts = CTSRunner.cts
start_time = cts.run("run cts -p android.aadb")
cts.get_result(start_time = start_time)
```

```python
import CTSRunner
cts = CTSRunner.cts
cts.results
cts.get_logs(session = 0)
cts.get_result(session = 0)
```
