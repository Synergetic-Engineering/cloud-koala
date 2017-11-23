# Cloud Koala
*Run Excel calculations in the cloud*

Cloud Koala packages [Koala](https://github.com/anthill/koala) (from [WeAreAnts](WeAreAnts)) within a [Serverless Framework](http://www.serverless.com) environment to deploy a AWS API Gateway REST API for converting Excel workbooks into python objects that can be run on AWS Lambda and serialized & stored on AWS S3 for on the fly calculation of the workbooks without the need for Excel.

## Proposed API

* `https://.../models`
    * GET - list of available calculations
    * POST - upload an Excel model to compile it into a Koala serialized python object, responds with the model's ID
* `https://.../models/{model_id}`
    * GET - model info
    * PUT - update model
    * POST - upload model input data, responds with results from the model
    * DELETE - remove model

## Requirements

* NPM
* Serverless Framework
* Docker (for serverless-python-requirements)

## Installation

Install the plugins required for serverless

```bash
npm install
```

## Deployment

Deploy using the Serverless Framework CLI like so:

```bash
sls deploy
```

## Development

Developing requires Python, we recommend using a virtualenv, for example:

```bash
virtualenv env
source env/bin/activate
pip install -r requirements
```

## Testing

Tox is used for unit testing and continuous integration, install it via `pip install tox` and run the unit tests using

```bash
tox
```

To run a single function, `sls invoke local` command can be used (ensure the virtualenv is activated if you're using that).

```bash
sls invoke local -f {function}
```

## Credit

This has been developed based on the nifty python library [Koala](https://github.com/anthill/koala), developed by 

## Licence

GNU GPLv3
