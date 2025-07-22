# utils.site_rules.py 

SITE_RULES = {
  "esgtoday.com": {
    "blocked_paths": ["/feed", "/sample-page", "/advertise-with-us", 
                               "/terms-of-service-cookies-and-privacy-policy", "/esg-newsletter", 
                               "/esg-whitepapers"]}, 
  "universityaffairs.ca": {
    "blocked_paths": ["/career-advice", "/subscribe-magazine", "/us", "/author",
                                          "/sponsored-content", "/article_topic/qa", "/profile", "/contact-us"]}, 
  "universityworldnews.com": {
    "allowed_paths": ["post.php"]},
    # "blocked_paths": ["/mbzuai-job.php", "/page.php?page=subscribe", "/jobs-hub", 
    #                               "page.php?page=sponsor", "page.php?page=Careers_at_UWN"]}, 
  "enterpriseriskmag.com": {}, 
  "chronicle.com": {
    "allowed_paths": ["/article"]},
    # "blocked_paths": ["/career-resources", "/events", "/podcast", "/package", "/professional-development",
    #                     "/professional-development-resources", "/author"]}
  "strategic-risk-global.com": {
    "allowed_paths": [".article"]
  },
  "cbc.ca": {
    "allowed_paths": ["/news/"], 
    "blocked_paths": ["/news/entertainment"]
  },
  "ctvnews.ca": {
    "allowed_paths": ["/article"]
  },
  "globalnews.ca": {
    "allowed_paths": ["/news"]
  }, 
  "mckinsey.com": {
    "blocked_paths": ["/how-we-help-clients", "/contact-us", "/scam-warning",
                      "/frequently-asked-questions", "/insights/rss.aspx"]
  }
}