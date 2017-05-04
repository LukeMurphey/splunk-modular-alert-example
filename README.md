# Splunk Modular Alert Action Example
This is an example of a modular alert in Splunk.

See the blog at https://www.splunk.com/blog/2016/08/22/how-to-create-a-modular-alert/ for instructions on how to write a modular alert action.

## FAQ

### How do I do something with the search results in the alert?

The search results are returned in the "payload" argument that is provided to the run() function.

Here is an example that retrieves the "source" field from the results:

    def run(self, cleaned_params, payload):
        
        # Get the "source" field of the search result from the payload
        source_field = payload['result'].get('source', 'source was undefined')
        self.logger.info("The source was: " + source_field)
 
