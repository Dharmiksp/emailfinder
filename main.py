from flask import request, Flask
from linkedin_api import Linkedin
from flask_cors import CORS


api = Linkedin('pateldharmik1504@gmail.com', '9099301502')
app = Flask(__name__)
CORS(app)


@app.route("/", methods=['GET'])
def dom():
    return "Hey There"


@app.route("/", methods=['POST'])
def data():
    payload = request.json
    companySlug = payload['company_slug']
    companyLink = api.get_company(companySlug)
    url1 = companyLink["callToAction"]
    domain1 = url1['url']
    domainSplitted = domain1.split("/")
    domainafterSplit = domainSplitted[2]

    if domainafterSplit.find("www.") != -1:
        domainWithwww = domainafterSplit.split(".")
        if len(domainWithwww) == 4:
            domain = domainWithwww[2] + "." + domainWithwww[3]
        else:
            domain = domainWithwww[1] + "." + domainWithwww[2]
    else:
        domain2 = domainafterSplit.split(".")
        if len(domain2) != 2:
            domain = domain2[1] + "." + domain2[2]
        else:
            domain = domainafterSplit

    fullName = payload['prospect_name']
    fullNameArray = fullName.split()
    firstName = fullNameArray[0]
    firstNameLower = firstName.lower()
    lastName = fullNameArray[1]
    lastNameLower = lastName.lower()
    firstNameInitialArray = [char for char in firstNameLower]
    firstNameInitial = firstNameInitialArray[0]
    lastNameInitialArray = [char for char in lastNameLower]
    lastNameInitial = lastNameInitialArray[0]

    def combination(fname, lname, domain, finitial, linitial):
        email1 = fname + "@" + domain
        email2 = fname + "." + lname + "@" + domain
        email3 = fname + lname + "@" + domain
        email4 = lname + "." + fname + "@" + domain
        email5 = lname + fname + "@" + domain
        email6 = fname + "." + linitial + "@" + domain
        email7 = finitial + "." + lname + "@" + domain
        email8 = linitial + "." + fname + "@" + domain
        email9 = lname + "." + finitial + "@" + domain
        email10 = lname + "@" + domain
        return [email1, email2, email3, email4, email5, email6, email7, email8, email9, email10]

    emailCombinations = combination(firstNameLower, lastNameLower, domain, firstNameInitial, lastNameInitial)
    
    return {"prospect_name": payload['prospect_name'], "company_slug": payload['company_slug'], "company_domain": domain, "email_combination": emailCombinations}

if __name__ == '__main__':
    app.run(debug=True)


