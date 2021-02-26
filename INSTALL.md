1. Choose your music folder:

```
Moo/play/config.py:

BASE ='/Users/steve/Music'
```

2. Clone the app:

```
$ git clone https://github.com/siznax/moo.git
```

3. Link your music folder:

```
$ cd moo/Moo/play/static
$ ln -s ${BASE} ./Moo
```

4. Start the app:

```
$ cd moo
$ ./play.sh
```

5. Visit `http://localhost:5000` in your browser

@siznax
