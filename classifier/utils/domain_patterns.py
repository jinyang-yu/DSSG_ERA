# Stores specific domain boilerplate patterns to remove by Regex
DOMAIN_PATTERNS = {
  "www.universityworldnews.com": [
        r"^Tweet$", 
        r"Receive email updates.*",  
        r"Global newsletters.*",     
        r"Sponsored Article$",  
        r"^Data will be processed according to our standard terms\s*&\s*conditions\s*\.$"
  ], 
  "www.esgtoday.com": [
        r"Mark founded ESG Today.*",  
        r"Related Posts.*",           
        r"Click here to access.*",    
        r"^\w+ \d{1,2}, \d{4}$",      
        r"^Mark Segal$"   
    ]
}