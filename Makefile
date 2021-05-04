clean:
	find app -name __pycache__ -type d -exec rm -rf {} \;
	rm -rf .aws-sam/

run-local:
	uvicorn app.main:app --port 8080 --reload

aws-validate:
	sam validate

aws-build : aws-validate
	sam build --use-container --debug

aws-package : aws-build
	sam package --s3-bucket my-travis-deployment-buck --output-template-file out.yml --region us-east-2

aws-deploy : aws-package
	sam deploy --template-file out.yml --stack-name fastapi-serverless-stack --region us-east-2 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM

