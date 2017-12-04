# Cloud Koala
*Run Excel calculations in the cloud* :cloud::koala:

[![LambCI Build Status](https://lambci-buildresults-x3wvacl759wh.s3-ap-southeast-2.amazonaws.com/gh/Synergetic-Engineering/cloud-koala/branches/master/26821f4cec821f75611edd3567f261a6.svg)](https://lambci-buildresults-x3wvacl759wh.s3-ap-southeast-2.amazonaws.com/gh/Synergetic-Engineering/cloud-koala/branches/master/371624d728e1605ae2aced95a05e3266.html)


Cloud Koala packages [Koala](https://github.com/anthill/koala) (from [WeAreAnts](http://weareants.fr/)) within a [Serverless Framework](http://www.serverless.com) environment to deploy a AWS API Gateway REST API for converting Excel workbooks into python objects that can be run on AWS Lambda and serialized & stored on AWS S3 for on the fly calculation of the workbooks without the need for Excel.

## API

* `https://.../models`
    * `GET` - list of available calculations
    * `POST` - upload an Excel model to compile it into a Koala serialized python object, responds with the model's ID
* `https://.../models/{model_id}`
    * `GET` - model info
    * `PUT` - update model
    * `POST` - upload model input data, responds with results from the model
    * `DELETE` - remove model
* `https://.../config`
    * `POST` - Add an auto-generated config sheet to a given Excel workbook

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

Developing requires Python, we recommend using a virtualenv, for example on linux, run:

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

And on windows, run:

```bash
python -m virtualenv env
env/Scripts/activate
pip install -r requirements.txt
```

It can also be useful to install the test requirements when developing

```bash
pip install -r lib/test/test_requirements.txt
```

## Testing locally

Tox is used for unit testing and continuous integration, install it via `pip install tox` and run the unit tests using

```bash
tox
```

To run a single function, `sls invoke local` command can be used (ensure the virtualenv is activated if you're using that).

```bash
sls invoke local -f {function}
```

## Testing the deployment

Mock events for `sls invoke` are in `test/mock_events`

To test a deployment, first add a model:
```bash
sls invoke --stage=dev --function=add_model --path=lib/test/mock_events/add_model.1.json
```

Check that the model has been added and compiled:
```bash
sls invoke --stage=dev --function=get_models --path=lib/test/mock_events/get_models.3.json
```

Generate model configuration data:
```bash
sls invoke --stage=dev --function=model_config --path=lib/test/mock_events/model_config.7.json
```

Add model with invalid model:
```bash
sls invoke --stage=dev --function=add_model --path=lib/test/mock_events/add_model.1a.json
```

Check that the model has been added and not compiled:
```bash
sls invoke --stage=dev --function=get_models --path=lib/test/mock_events/get_models.3.json
```

Next, update a model with a known `model_id`:
```bash
sls invoke --stage=dev --function=update_model --path=lib/test/mock_events/update_model.2.json
```

Get all models and check that both models have been created:
```bash
sls invoke --stage=dev --function=get_models --path=lib/test/mock_events/get_models.3.json
```

Get specific model with known `model_id`:
```bash
sls invoke --stage=dev --function=get_model --path=lib/test/mock_events/get_model.4.json
```

Run model with known `model_id`:
```bash
sls invoke --stage=dev --function=run_model --path=lib/test/mock_events/run_model.5.json
```

Finally, delete model with known `model_id`:
```bash
sls invoke --stage=dev --function=delete_model --path=lib/test/mock_events/delete_model.6.json
```

(The models created using `add_model` will not be deleted in this process)


## Credit

This project has been inspired by the nifty python library [Koala](https://github.com/anthill/koala) :koala: ([koala2](https://pypi.python.org/pypi/koala2) on pypi) developed by [WeAreAnts](http://weareants.fr/) :ant: that brought together the useful [Pycel](https://github.com/dgorissen/pycel) and [OpenPyXL](http://openpyxl.readthedocs.io/en/default/) libraries.

Thanks also to the developers of the [Serverless Framework](http://www.serverless.com), [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements) and [lambci](https://github.com/lambci/lambci).

## Licence

GPL-3.0
