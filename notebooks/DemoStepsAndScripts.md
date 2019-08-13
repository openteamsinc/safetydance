---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.2.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
from llstep import Context, ContextKey, script, step

ONE = ContextKey(int, "one")
TWO = ContextKey(int, "two")

@step
def step_one(context: Context):
    context[ONE] = 1

@step
def step_two(context: Context):
    context[TWO] = 2
    
@step
def step_with_args(context: Context, arg1, arg2=None):
    print("arg1", arg1, "arg2", arg2)
    print(context[ONE], context[TWO])
    step_one(context)
    
@script
def my_script():
    step_one()
    step_two()
    step_with_args("no keyword arg provided")
    step_with_args("keyword arg provided", arg2="this is the keyword arg")
    
my_script()
```

Next up, we'll add the use of type extension to add steps to Given, When, Then, And

```python
from llstep.bdd import Feature, Scenario, Given, When, Then, And
from llstep.bdd import http
import my_http

@Feature
def A_simple_web_api():
    """
    Describe the feature
    """
    
    @Scenario
    def get_resource():
        """
        Describe the scenario
        """
        When.http.get("https://example.com/does-not-exist")
        Then.http.status_is(404)
        
    @ScenarioOutline
    def get_resource_variations(url, expected_status):
        When.http.get(url)
        Then.http.status_is(expected_status)
        Then.http.print_status()
        
        with Examples("Resources that exist"):
            yield "https://foo.com/1", 200
            yield "https://foo.com/2", 200
        
        with Examples("Resources that are forbidden"):
            yield "https://foo.com/3", 403
            yield "https://foo.com/4", 403
            
```

```python
from llstep.bdd import Feature, Scenario, Given, When, Then, And
from llstep.bdd import http


@Feature
def A_simple_web_api():
    """
    Big description
    """

    with Scenario("Successful GET resource", description=""" say stuff """):
        """
        Scenario doc
        """
        When.http.get("https://example.com/does-not-exist")
        Then.http.status_is(404)
        
    with ScenarioOutline("HTTP GET variations", url, expected_status):
        a = "Foo"
        When.http.get(url)
        Then.http.status_is(expected_status)
        Then.http.resouce_as_json.has_key(a)
        
        with Examples("Resources that exist"):
            yield "https://foo.com/1", 200
            yield "https://foo.com/2", 200
        
        with Examples("Resources that are forbidden"):
            yield "https://foo.com/3", 403
            yield "https://foo.com/4", 403
            
        @Examples
        def sophisticated_examples():
            # do some real python things
            # then, do some yielding
            for item in items:
                yield item.key, item.value

            
```

```python
def foo():
    1, 2
    3, 4
    
foo()
```

```python
#ogdl
Feature "A simple web API"
    Scenario "Successful GET resource"
        description "Scenario documentation"
        When http GET "/https://example.com/does-not-exist"
        Then http status_is 404
        
        escapeto: Python
            for x in range()
```
