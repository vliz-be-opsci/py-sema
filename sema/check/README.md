Yaml for tests will look like

```yaml
- url: "http://example.com"
  type: "example"
  options:
    param1: "value1"
    param2: "value2"
- url: "http://another.com"
  type: "another_test"
  options:
    paramA: "valueA"
```

where `url` is the URL to test, `type` is the test type, and `options` are the test parameters.

## Testing base class

The TestBase is a dataclass that holds the test data. It has the following fields:

- `url` - the URL to test
- `type` - the test type
- `options` - the test parameters
- `result` - the test result
  - `success`: boolean, whether the test was successful
  - `message`: string, a message describing the test result, this can also be the error message
  - `error`: boolean, whether the test failed due to an error

## flow of sema-check

```mermaid
graph TD
    A[User] -->|Invokes CLI| B["CLI Module (__main__.py)"]
    B --> C["Argument Parser"]
    C --> D["Service Module (service.py)"]
    D --> E["Load YAML Files"]
    D --> F["Instantiate Test Classes"]
    F --> G["Test Classes (tests/)"]
    G --> H["Execute Tests"]
    H --> I["Collect Test Results"]
    I --> J["Sink Modules (sinks/)"]
    J --> K["CSV Sink (csv_sink.py)"]
    J --> L["HTML Sink (html_sink.py)"]
    J --> M["YML Sink (yml_sink.py)"]
    K --> N["Output: results.csv"]
    L --> O["Output: results.html"]
    M --> P["Output: results.yml"]
    D --> Q["Utilities (utils.py)"]
    Q --> R["Utility Functions"]

    %% Styling Nodes
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bfb,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
    style G fill:#fbf,stroke:#333,stroke-width:2px
    style H fill:#fbf,stroke:#333,stroke-width:2px
    style I fill:#fbb,stroke:#333,stroke-width:2px
    style J fill:#ffb,stroke:#333,stroke-width:2px
    style K fill:#bff,stroke:#333,stroke-width:2px
    style L fill:#bff,stroke:#333,stroke-width:2px
    style M fill:#bff,stroke:#333,stroke-width:2px
    style N fill:#cff,stroke:#333,stroke-width:2px
    style O fill:#cff,stroke:#333,stroke-width:2px
    style P fill:#cff,stroke:#333,stroke-width:2px
    style Q fill:#fdf,stroke:#333,stroke-width:2px
    style R fill:#dfd,stroke:#333,stroke-width:2px
```
