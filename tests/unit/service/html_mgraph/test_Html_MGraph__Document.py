from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Document import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base     import Html_MGraph__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Head     import Html_MGraph__Head
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Body     import Html_MGraph__Body
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Attributes import Html_MGraph__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Scripts  import Html_MGraph__Scripts
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Styles   import Html_MGraph__Styles
from mgraph_db.mgraph.schemas.identifiers.Node_Path                         import Node_Path
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id           import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id            import Obj_Id
from osbot_utils.utils.Objects                                              import base_classes


class test_Html_MGraph__Document(TestCase):                                     # Test document orchestrator

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Document() as _:
            assert type(_)          is Html_MGraph__Document
            assert base_classes(_)  == [Html_MGraph__Base, Type_Safe, object]
            assert _.head_graph     is None
            assert _.body_graph     is None
            assert _.attrs_graph    is None
            assert _.scripts_graph  is None
            assert _.styles_graph   is None
            assert _.PREDICATE_GRAPH is not None
            assert _.PATH_HTML       == 'html'

    def test_setup(self):                                                       # Test setup initializes all graphs
        with Html_MGraph__Document().setup() as _:
            assert _.mgraph is not None
            assert _.root_id is not None

    def test_setup_initializes_all_graphs(self):                                # Test setup creates all component graphs
        with Html_MGraph__Document().setup() as _:
            assert _.head_graph     is not None
            assert _.body_graph     is not None
            assert _.attrs_graph    is not None
            assert _.scripts_graph  is not None
            assert _.styles_graph   is not None

            assert type(_.head_graph)    is Html_MGraph__Head
            assert type(_.body_graph)    is Html_MGraph__Body
            assert type(_.attrs_graph)   is Html_MGraph__Attributes
            assert type(_.scripts_graph) is Html_MGraph__Scripts
            assert type(_.styles_graph)  is Html_MGraph__Styles

    def test_setup_initializes_component_roots(self):                           # Test each component graph has its root
        with Html_MGraph__Document().setup() as _:
            assert _.head_graph   .root_id is not None
            assert _.body_graph   .root_id is not None
            assert _.attrs_graph  .root_id is not None
            assert _.scripts_graph.root_id is not None
            assert _.styles_graph .root_id is not None

    def test_setup_registers_html_element(self):                                # Test setup registers <html> in attrs_graph
        with Html_MGraph__Document().setup() as _:
            tag = _.attrs_graph.get_tag(_.root_id)
            assert tag == 'html'

    def test_setup_creates_graph_links(self):                                   # Test setup creates edges to component graphs
        with Html_MGraph__Document().setup() as _:
            outgoing = _.outgoing_edges(_.root_id)
            assert len(outgoing) == 5                                           # head, body, attrs, scripts, styles

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Tests - Tags
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_tag(self):                                                     # Test getting tag via document
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'div')

            assert _.get_tag(node_id) == 'div'

    def test_get_tag__html_root(self):                                          # Test getting tag for document root
        with Html_MGraph__Document().setup() as _:
            assert _.get_tag(_.root_id) == 'html'

    def test_get_tag__not_found(self):                                          # Test getting tag for non-registered element
        with Html_MGraph__Document().setup() as _:
            fake_id = Node_Id(Obj_Id())
            assert _.get_tag(fake_id) is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Tests - Attributes
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_attributes(self):                                              # Test getting attributes via document
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'div')
            _.attrs_graph.add_attribute(node_id, 'class', 'container', position=0)
            _.attrs_graph.add_attribute(node_id, 'id'   , 'main'     , position=1)

            attrs = _.get_attributes(node_id)
            assert attrs == {'class': 'container', 'id': 'main'}

    def test_get_attributes__empty(self):                                       # Test getting attributes when none set
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'br')

            attrs = _.get_attributes(node_id)
            assert attrs == {}

    def test_get_attribute(self):                                               # Test getting single attribute
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'a')
            _.attrs_graph.add_attribute(node_id, 'href', 'https://test.com', position=0)

            assert _.get_attribute(node_id, 'href') == 'https://test.com'

    def test_get_attribute__not_found(self):                                    # Test getting non-existent attribute
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'div')

            assert _.get_attribute(node_id, 'nonexistent') is None

    def test_get_elements_by_tag(self):                                         # Test getting elements by tag
        with Html_MGraph__Document().setup() as _:
            div1 = Node_Id(Obj_Id())
            div2 = Node_Id(Obj_Id())
            p1   = Node_Id(Obj_Id())

            _.attrs_graph.register_element(div1, 'div')
            _.attrs_graph.register_element(div2, 'div')
            _.attrs_graph.register_element(p1  , 'p')

            divs = _.get_elements_by_tag('div')
            assert len(divs) == 2
            assert div1 in divs
            assert div2 in divs

    def test_get_elements_by_tag__not_found(self):                              # Test getting elements for non-existent tag
        with Html_MGraph__Document().setup() as _:
            result = _.get_elements_by_tag('nonexistent')
            assert result == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Tests - Scripts
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_script_content(self):                                          # Test getting script content
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.scripts_graph.register_script(script_id, content="console.log('test');")

            content = _.get_script_content(script_id)
            assert content == "console.log('test');"

    def test_get_script_content__external(self):                                # Test getting content for external script
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.scripts_graph.register_script(script_id, content=None)

            content = _.get_script_content(script_id)
            assert content is None

    def test_get_script_content__not_found(self):                               # Test getting content for non-registered script
        with Html_MGraph__Document().setup() as _:
            fake_id = Node_Id(Obj_Id())
            content = _.get_script_content(fake_id)
            assert content is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Tests - Styles
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_style_content(self):                                           # Test getting style content
        with Html_MGraph__Document().setup() as _:
            style_id = Node_Id(Obj_Id())
            _.styles_graph.register_style(style_id, content=".container { display: flex; }")

            content = _.get_style_content(style_id)
            assert content == ".container { display: flex; }"

    def test_get_style_content__external(self):                                 # Test getting content for external stylesheet
        with Html_MGraph__Document().setup() as _:
            link_id = Node_Id(Obj_Id())
            _.styles_graph.register_link(link_id)

            content = _.get_style_content(link_id)
            assert content is None

    def test_get_style_content__not_found(self):                                # Test getting content for non-registered style
        with Html_MGraph__Document().setup() as _:
            fake_id = Node_Id(Obj_Id())
            content = _.get_style_content(fake_id)
            assert content is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Tests - Text Content
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_text_content__body(self):                                      # Test getting text content from body
        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.create_text(text='Hello World', parent_id=div_id)

            content = _.get_text_content(div_id, in_head=False)
            assert content == 'Hello World'

    def test_get_text_content__head(self):                                      # Test getting text content from head
        with Html_MGraph__Document().setup() as _:
            title_id = Node_Id(Obj_Id())
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.create_text(text='Page Title', parent_id=title_id)

            content = _.get_text_content(title_id, in_head=True)
            assert content == 'Page Title'

    def test_get_text_content__empty(self):                                     # Test getting text when none exists
        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)

            content = _.get_text_content(div_id)
            assert content == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Info Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_element_info(self):                                                # Test getting element info
        with Html_MGraph__Document().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(node_id, 'div')
            _.attrs_graph.add_attribute(node_id, 'class', 'container', position=0)

            info = _.element_info(node_id)

            assert info['node_id']    == str(node_id)
            assert info['tag']        == 'div'
            assert info['attributes'] == {'class': 'container'}

    def test_element_info__script_with_content(self):                           # Test element info for script with content
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(script_id, 'script')
            _.scripts_graph.register_script(script_id, content="alert('hi');")

            info = _.element_info(script_id)

            assert info['tag']            == 'script'
            assert info['script_content'] == "alert('hi');"

    def test_element_info__script_external(self):                               # Test element info for external script (no content)
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(script_id, 'script')
            _.attrs_graph.add_attribute(script_id, 'src', 'app.js', position=0)
            _.scripts_graph.register_script(script_id, content=None)

            info = _.element_info(script_id)

            assert info['tag']             == 'script'
            assert 'script_content' not in info                                 # No content for external

    def test_element_info__style_with_content(self):                            # Test element info for style with content
        with Html_MGraph__Document().setup() as _:
            style_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(style_id, 'style')
            _.styles_graph.register_style(style_id, content="body { margin: 0; }")

            info = _.element_info(style_id)

            assert info['tag']           == 'style'
            assert info['style_content'] == "body { margin: 0; }"

    def test_element_info__style_external(self):                                # Test element info for external style (no content)
        with Html_MGraph__Document().setup() as _:
            link_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(link_id, 'style')
            _.styles_graph.register_style(link_id, content=None)

            info = _.element_info(link_id)

            assert info['tag']            == 'style'
            assert 'style_content' not in info

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Traversal Tests - Body
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_body_children(self):                                           # Test getting body children
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.add_child(body_root, div_id, position=0)

            children = _.get_body_children(body_root)
            assert children == [div_id]

    def test_get_body_children__empty(self):                                    # Test getting body children when none exist
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            children  = _.get_body_children(body_root)
            assert children == []

    def test_walk_body(self):                                                   # Test walking body tree
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())
            p_id      = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.p'), node_id=p_id)
            _.body_graph.add_child(body_root, div_id, position=0)
            _.body_graph.add_child(div_id   , p_id  , position=0)

            _.attrs_graph.register_element(div_id, 'div')
            _.attrs_graph.register_element(p_id  , 'p')

            result = _.walk_body()

            assert len(result) == 3                                             # body root, div, p
            tags = [item['tag'] for item in result if item['tag']]
            assert 'div' in tags
            assert 'p'   in tags

    def test_walk_body__from_node(self):                                        # Test walking body from specific node
        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            span_id = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.span'), node_id=span_id)
            _.body_graph.add_child(_.body_graph.root_id, div_id, position=0)
            _.body_graph.add_child(div_id, span_id, position=0)

            _.attrs_graph.register_element(div_id , 'div')
            _.attrs_graph.register_element(span_id, 'span')

            result = _.walk_body(div_id)

            assert len(result) == 2                                             # div, span
            tags = [item['tag'] for item in result]
            assert 'div'  in tags
            assert 'span' in tags

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Traversal Tests - Head
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_head_children(self):                                           # Test getting head children
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta'), node_id=meta_id)
            _.head_graph.add_child(head_root, meta_id, position=0)

            children = _.get_head_children(head_root)
            assert children == [meta_id]

    def test_get_head_children__empty(self):                                    # Test getting head children when none exist
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            children  = _.get_head_children(head_root)
            assert children == []

    def test_walk_head(self):                                                   # Test walking head tree
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())
            title_id  = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta') , node_id=meta_id)
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.add_child(head_root, meta_id , position=0)
            _.head_graph.add_child(head_root, title_id, position=1)

            _.attrs_graph.register_element(meta_id , 'meta')
            _.attrs_graph.register_element(title_id, 'title')

            result = _.walk_head()

            assert len(result) == 3                                             # head root, meta, title
            tags = [item['tag'] for item in result if item['tag']]
            assert 'meta'  in tags
            assert 'title' in tags

    def test_walk_head__from_node(self):                                        # Test walking head from specific node
        with Html_MGraph__Document().setup() as _:
            title_id = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.add_child(_.head_graph.root_id, title_id, position=0)

            _.attrs_graph.register_element(title_id, 'title')

            result = _.walk_head(title_id)

            assert len(result) == 1
            assert result[0]['tag'] == 'title'

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test comprehensive stats
        with Html_MGraph__Document().setup() as _:
            stats = _.stats()

            assert 'document'   in stats
            assert 'head'       in stats
            assert 'body'       in stats
            assert 'attributes' in stats
            assert 'scripts'    in stats
            assert 'styles'     in stats

    def test_stats__document_section(self):                                     # Test document section of stats
        with Html_MGraph__Document().setup() as _:
            stats = _.stats()

            doc_stats = stats['document']
            assert 'total_nodes' in doc_stats
            assert 'total_edges' in doc_stats
            assert doc_stats['root_id'] == str(_.root_id)

    def test_stats__component_sections(self):                                   # Test component sections have expected keys
        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(div_id, 'div')
            _.attrs_graph.add_attribute(div_id, 'class', 'test', position=0)

            stats = _.stats()

            assert stats['attributes']['tag_nodes']     >= 1
            assert stats['attributes']['element_nodes'] >= 1
            assert stats['attributes']['attr_nodes']    >= 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_to_json(self):                                                     # Test JSON export
        with Html_MGraph__Document().setup() as _:
            json_data = _.to_json()

            assert type(json_data)    is dict
            assert 'document'         in json_data
            assert 'head'             in json_data
            assert 'body'             in json_data
            assert 'attributes'       in json_data
            assert 'scripts'          in json_data
            assert 'styles'           in json_data

    def test_to_json__all_dicts(self):                                          # Test all sections are dicts
        with Html_MGraph__Document().setup() as _:
            json_data = _.to_json()

            assert type(json_data['document'])   is dict
            assert type(json_data['head'])       is dict
            assert type(json_data['body'])       is dict
            assert type(json_data['attributes']) is dict
            assert type(json_data['scripts'])    is dict
            assert type(json_data['styles'])     is dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_document_workflow(self):                                      # Test complete document workflow
        with Html_MGraph__Document().setup() as _:
            # Register elements in attrs_graph
            html_id  = _.root_id                                                # Already registered in setup
            head_id  = _.head_graph.root_id
            body_id  = _.body_graph.root_id
            meta_id  = Node_Id(Obj_Id())
            title_id = Node_Id(Obj_Id())
            div_id   = Node_Id(Obj_Id())
            script_id = Node_Id(Obj_Id())

            # Register tags
            _.attrs_graph.register_element(meta_id  , 'meta')
            _.attrs_graph.register_element(title_id , 'title')
            _.attrs_graph.register_element(div_id   , 'div')
            _.attrs_graph.register_element(script_id, 'script')

            # Add attributes
            _.attrs_graph.add_attribute(_.root_id, 'lang', 'en', position=0)
            _.attrs_graph.add_attribute(meta_id  , 'charset', 'utf-8', position=0)
            _.attrs_graph.add_attribute(div_id   , 'class', 'container', position=0)
            _.attrs_graph.add_attribute(script_id, 'src', 'app.js', position=0)

            # Build head structure
            _.head_graph.create_element(node_path=Node_Path('head.meta') , node_id=meta_id)
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.add_child(head_id, meta_id , position=0)
            _.head_graph.add_child(head_id, title_id, position=1)
            _.head_graph.create_text(text='My Page', parent_id=title_id)

            # Build body structure
            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.script'), node_id=script_id)
            _.body_graph.add_child(body_id, div_id   , position=0)
            _.body_graph.add_child(body_id, script_id, position=1)
            _.body_graph.create_text(text='Hello World', parent_id=div_id)

            # Register script
            _.scripts_graph.register_script(script_id, content=None)            # External script

            # Verify cross-graph queries
            assert _.get_tag(_.root_id)        == 'html'
            assert _.get_tag(div_id)           == 'div'
            assert _.get_attribute(_.root_id, 'lang') == 'en'
            assert _.get_attribute(meta_id, 'charset') == 'utf-8'

            # Verify text content
            assert _.get_text_content(title_id, in_head=True) == 'My Page'
            assert _.get_text_content(div_id, in_head=False)  == 'Hello World'

            # Verify element info
            div_info = _.element_info(div_id)
            assert div_info['tag']        == 'div'
            assert div_info['attributes'] == {'class': 'container'}

            # Verify tree walking
            head_elements = _.walk_head()
            body_elements = _.walk_body()
            assert len(head_elements) >= 3                                      # head, meta, title
            assert len(body_elements) >= 3                                      # body, div, script

            # Verify stats
            stats = _.stats()
            assert stats['attributes']['tag_nodes'] >= 4                        # meta, title, div, script (html is also there)