# webapps2024

 ### 1. Creating virtual environment
`python -m venv venv`
### 2. Activating virtual environment 
#### On windows 
`venv/Scripts/activate`
    
#### on linux/ubuntu
 `source venv/bin/activate`

### 3. Installing requirements
`pip install -r requirements.txt`

### 4. running thrift timestamp
`./thrift-0.20.0.exe -gen py timestamp_service.thrift`
