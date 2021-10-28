from api_watchdog.collect import WatchdogResultGroup
from api_watchdog.core import WatchdogResult, ExpectationResult

def html_from_result_group(result_group: WatchdogResultGroup) -> str:
    def group_format(result_group: WatchdogResultGroup):
        html = (
            f'<h2>{result_group.name}</h2>'
        )
        for result in sorted(result_group.results, key=lambda g: g.test_name):
            html += result_format(result)

        for child_result_group in sorted(result_group.groups, key=lambda g: g.name):
            html += group_format(child_result_group)

        return html

    def result_format(result: WatchdogResult) -> str:
        passed = "Pass" if result.success else "Fail"
        html = (
            f'<h3>{result.test_name}: {passed} ({result.latency:.3f}s)</h3>\n'
            f'<div class="expectations">\n'
        )
        for expectation_result in result.results:
            html += expectation_result_format(expectation_result)
        html += (
            f'</div>\n'
        )
        return html

    def expectation_result_format(expectation_result: ExpectationResult) -> str:
        class_name = "passed" if expectation_result.result == "success" else "failed"
        html = (
            f'<div class="result {class_name}">\n'
            f'  <p>{expectation_result.expectation.selector}</p>\n'
            f'  <p>({expectation_result.expectation.validation_type.value}){expectation_result.expectation.value}</p>\n'
            f'  <p>{expectation_result.actual}</p>\n'
            f'</div>'
        )
        return html

    html = """
<html>
  <head>
    <title>
      Watchdog Test Report
    </title>
    <style type="text/css">
    body{
      margin:40px auto;
      max-width:650px;
      line-height:1.6;
      font-size:18px;
      color:#444;
      padding:0 10px;
    }
    h1, h2, h3 {
      line-height:1.2;
    }
    code {
      border: 1px solid #ddd;
      background-color: #f8f8f8;
      font-family:'Lucida Console', monospace;
    }
    .result {
      font-size: 12px;
      padding-left: 16px;
      border-radius: 8px;
      border: 1px solid #ddd;
      font-family:'Lucida Console', monospace;
    }
    .passed {
      background-color: #dbfad9;
    }

    .failed {
      background-color: #fadad9;
    }
    </style>
  </head>
  <body>
  <h1>Watchdog Results Report</h1>
    """

    html += group_format(result_group)

    html += """
  </body>
</html>
"""

    return html
