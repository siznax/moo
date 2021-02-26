Moo Development
===============

See https://docs.python-guide.org/starting/installation/


Mac OS X
--------

1. Install **Apple Command Line Tools** to build python

Accept license and install Xcode

```
$ sudo xcode-select install
```

2. Install `python` with **Homebrew**

```
$ brew install python
```

```
$ which python3
/usr/local/bin/python3
```

```
$ python3 --version
Python 3.9.1
```

```
$ python3 -m site --user-base
/Users/steve/Library/Python/3.9
```

3. Ensure `pip3` **package installer** is available

_I had a copy of `/usr/local/bin/pip` that I had to remove, probably
from a previous (python 2) installation._

```
$ which pip3
/usr/local/bin/pip
```

```
$ pip3 --version
pip 20.3.1 from 
/usr/local/lib/python3.9/site-packages/pip (python 3.9)
```

4. Install `virtualenv` **dependency manager** to isolate your
   python apps from other environments

```
$ pip3 install virtualenv virtualenvwrapper
```

```
$ virtualenv --version
virtualenv 20.2.2 from
/usr/local/lib/python3.9/site-packages/virtualenv/__init__.py
```

5. Create a `venv` for your project

```
$ mkvirtualenv --python=`which python3` moo
```

```
[moo]$ which python
/Users/steve/.virtualenvs/moo/bin/python
```

```
[moo]$ python --version
Python 3.9.1
```

6. Work on project

```
$ workon moo
[moo]$ 
```

To remove a `venv`...

```
[moo]$ deactivate
`$ rmvirtualenv moo
```


@siznax
