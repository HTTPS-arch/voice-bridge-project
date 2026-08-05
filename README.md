# Machine Translation Module

## Overview

This module performs text translation using **Deep Translator (Google Translate)**. It translates text from the source language to the target language configured in `config.py`.

## Translator

- Deep Translator
- Google Translate

## Features

- Fast Text Translation
- Lightweight Implementation
- Configurable Source and Target Languages
- Easy Integration with Other Modules
- Simple Python-Based Translation Module

## Project Files

- `translator.py` - Translation module
- `config.py` - Language configuration
- `requirements.txt` - Project dependencies

## Requirements

- Python 3.x
- deep-translator

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python translator.py
```

## Configuration

Configure the translation languages in `config.py`.

```python
SOURCE_LANGUAGE = "en"
TARGET_LANGUAGE = "te"
```