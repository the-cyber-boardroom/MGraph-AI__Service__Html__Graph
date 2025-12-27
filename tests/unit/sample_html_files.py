def generate__test_html(element_count: int) -> str:          # Generate HTML with N div elements, each with attributes
    items = "\n".join(
        f'        <div class="item item-{i}" data-id="{i}" data-type="widget">'
        f'<span class="label">Item {i}</span></div>'
        for i in range(element_count)
    )
    return f'''<html lang="en">
    <head><title>Scaled Test ({element_count} elements)</title></head>
    <body class="container">
        <div class="items">{items}</div>
    </body>
</html>'''

SIMPLE_HTML = '<html><body><div class="main" id="content">Hello World</div></body></html>'

NESTED_HTML = '''
<html>
    <body>
        <div class="main" id="content">
            <h1>Title</h1>
            <p>Paragraph</p>
        </div>
    </body>
</html>'''

HTML__WITH_ONE_PARAGRAPH = "<html><body><p>an paragraph</p></body></html>"

HTML__WITH_SOME_TAGS = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Test Page</title>
    </head>
    <body>
        <h1>Hello World</h1>
        <div>
            <p>This is a test paragraph.</p>
            <p>This is the 2nd paragraph.</p>
        </div>
        <div>
            another div with <b>a bold</b> element
        </div>
    </body>
</html>"""

HTML__BOOTSTRAP_EXAMPLE = """
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Bootstrap Example</title>
        <link href="bootstrap.min.css" rel="stylesheet" />
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="#">Brand</a>
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link" href="#">Home</a></li>
                </ul>
            </div>
        </nav>
    </body>
</html>
"""