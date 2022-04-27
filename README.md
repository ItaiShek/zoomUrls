<!-- Badges -->
[![](https://img.shields.io/github/v/release/ItaiShek/zoomUrls)](https://github.com/ItaiShek/zoomUrls/releases)
![](https://img.shields.io/github/downloads/ItaiShek/zoomUrls/total?color=red)
[![](https://img.shields.io/github/issues/ItaiShek/zoomUrls?color=yellow)](https://github.com/ItaiShek/zoomUrls/issues)
[![](https://img.shields.io/github/license/ItaiShek/zoomUrls?label=license&color=green)](https://github.com/ItaiShek/zoomUrls/blob/main/LICENSE)

# General info

zoomUrls is a software meant for HIT students, to generate a list of all zoom cloud recordings from moodle.

## Usage
```
usage: zoomUrls -u USERNAME -p PASSWORD URL [URL1 URL2...]

 e.g.: zoomUrls -u student -p pass123 https://md.hit.ac.il/course/view.php?id=12345

positional arguments:
  URL               The course/s url/s you want to scrape

optional arguments:
  -h, --help        show this help message and exit
  -u, --username    Your moodle username
  -p, --password    Your moodle password
  -v, --verbose     Print debugging information
  -o, --output      Save the urls to a csv file
  -a, --user-agent  Override the default user agent
```

## Installation

<details>

<summary style="font-size:large">Linux</summary>

#### Method 1: Using curl 

```bash
sudo curl -L https://github.com/ItaiShek/zoomUrls/releases/download/v1.0.1/zoomUrls -o /usr/local/bin/zoomUrls
sudo chmod a+rx /usr/local/bin/zoomUrls
```

#### Method 2: Using wget

```bash
sudo wget https://github.com/ItaiShek/zoomUrls/releases/download/v1.0.1/zoomUrls -O /usr/local/bin/zoomUrls
sudo chmod a+rx /usr/local/bin/zoomUrls
```

#### Method 3: Direct download

Download it from [here](https://github.com/ItaiShek/zoomUrls/releases/download/v1.0.1/zoomUrls).

#### Method 4: Clone repository

Requires: python >= 3.6

```bash
git clone https://github.com/ItaiShek/zoomUrls.git && cd zoomUrls
python -m pip install -r requirements.txt
```

</details>


<details>

<summary style="font-size:large">Windows</summary>

#### Direct download

Download it from [here](https://github.com/ItaiShek/zoomUrls/releases/download/v1.0.1/zoomUrls.exe).

Add the file to any folder except "C:\Windows\System32", and add it to [PATH](https://docs.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)).

</details>


