# utils.site_rules.py 

SITE_RULES = {
  "esgtoday.com": {
    "blocked_paths": ["/feed", "/sample-page", "/advertise-with-us", 
                               "/terms-of-service-cookies-and-privacy-policy", "/esg-newsletter", 
                               "/esg-whitepapers"]}, 
  "universityaffairs.ca/category/news": {
    "blocked_paths": ["/career-advice", "/subscribe-magazine", "/us", 
                                          "/sponsored-content", "/article_topic/qa"]}, 
  "universityworldnews.com": {
    "allowed_paths": ["post.php"]},
    # "blocked_paths": ["/mbzuai-job.php", "/page.php?page=subscribe", "/jobs-hub", 
    #                               "page.php?page=sponsor", "page.php?page=Careers_at_UWN"]}, 
  "enterpriseriskmag.com/latest-articles": {}, 
  "chronicle.com": {
    "allowed_paths": ["/article"]},
    # "blocked_paths": ["/career-resources", "/events", "/podcast", "/package", "/professional-development",
    #                     "/professional-development-resources", "/author"]}
  "strategic-risk-global.com/risk-type": {
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
  "mckinsey.com/capabilities/risk-and-resilience/our-insights": {
    "blocked_paths": ["/how-we-help-clients"]
  }
}