# pephubgen
Generate a tree of static files that can be served by any file server to download and fetch information from any PEP project storage repository. By defualt, `pephubgen` will utilize the official one stored [here](https://github.com/pepkit/data.pephub).

## Installation
To install, clone this repository and install with `pip`:

```sh
git clone git@github.com:pepkit/pephubgen.git
pip install .
```

Once complete, you can then run the file tree generator from the command line with:

```
pephubgen --out <output_path>
```

You can then view a **development** version of the file tree using python's built-in http server or the script provided with this repo:

```
pephubgen --out ./output
pephubgen serve --files ./output
```

or

```
pephubgen --out ./output
./serve output
```
