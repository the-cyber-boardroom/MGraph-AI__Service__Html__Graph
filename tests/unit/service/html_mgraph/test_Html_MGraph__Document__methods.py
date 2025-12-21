from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Document import Html_MGraph__Document
from mgraph_db.mgraph.schemas.identifiers.Node_Path                         import Node_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id           import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id            import Obj_Id


class test_Html_MGraph__Document__Methods(TestCase):                            # Test Document methods for code coverage

    # ═══════════════════════════════════════════════════════════════════════════
    # element_info Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_element_info__basic(self):                                         # Test element_info for basic element
        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(div_id, 'div')
            _.attrs_graph.add_attribute(div_id, 'class', 'container', position=0)
            _.attrs_graph.add_attribute(div_id, 'id'   , 'main'     , position=1)

            info = _.element_info(div_id)

            assert info['node_id']    == str(div_id)
            assert info['tag']        == 'div'
            assert info['attributes'] == {'class': 'container', 'id': 'main'}
            assert 'script_content' not in info
            assert 'style_content'  not in info

    def test_element_info__script_with_content(self):                           # Test element_info for script with inline content
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(script_id, 'script')
            _.attrs_graph.add_attribute(script_id, 'type', 'text/javascript', position=0)
            _.scripts_graph.register_script(script_id, content="console.log('test');")

            info = _.element_info(script_id)

            assert info['tag']            == 'script'
            assert info['attributes']     == {'type': 'text/javascript'}
            assert info['script_content'] == "console.log('test');"

    def test_element_info__script_external(self):                               # Test element_info for external script (no content)
        with Html_MGraph__Document().setup() as _:
            script_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(script_id, 'script')
            _.attrs_graph.add_attribute(script_id, 'src', 'app.js', position=0)
            _.scripts_graph.register_script(script_id, content=None)

            info = _.element_info(script_id)

            assert info['tag']             == 'script'
            assert info['attributes']      == {'src': 'app.js'}
            assert 'script_content' not in info                                 # No content key for external

    def test_element_info__style_with_content(self):                            # Test element_info for style with inline content
        with Html_MGraph__Document().setup() as _:
            style_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(style_id, 'style')
            _.attrs_graph.add_attribute(style_id, 'type', 'text/css', position=0)
            _.styles_graph.register_style(style_id, content="body { margin: 0; }")

            info = _.element_info(style_id)

            assert info['tag']           == 'style'
            assert info['attributes']    == {'type': 'text/css'}
            assert info['style_content'] == "body { margin: 0; }"

    def test_element_info__style_external(self):                                # Test element_info for external style (no content)
        with Html_MGraph__Document().setup() as _:
            style_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(style_id, 'style')
            _.styles_graph.register_style(style_id, content=None)

            info = _.element_info(style_id)

            assert info['tag']            == 'style'
            assert 'style_content' not in info                                  # No content key for external

    def test_element_info__no_attributes(self):                                 # Test element_info for element without attributes
        with Html_MGraph__Document().setup() as _:
            br_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(br_id, 'br')

            info = _.element_info(br_id)

            assert info['tag']        == 'br'
            assert info['attributes'] == {}

    def test_element_info__non_registered(self):                                # Test element_info for non-registered element
        with Html_MGraph__Document().setup() as _:
            fake_id = Node_Id(Obj_Id())

            info = _.element_info(fake_id)

            assert info['node_id']    == str(fake_id)
            assert info['tag']        is None
            assert info['attributes'] == {}

    # ═══════════════════════════════════════════════════════════════════════════
    # get_body_children Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_body_children__single(self):                                   # Test getting single body child
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.add_child(body_root, div_id, position=0)

            children = _.get_body_children(body_root)

            assert children == [div_id]

    def test_get_body_children__multiple(self):                                 # Test getting multiple body children
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            header_id = Node_Id(Obj_Id())
            main_id   = Node_Id(Obj_Id())
            footer_id = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.header'), node_id=header_id)
            _.body_graph.create_element(node_path=Node_Path('body.main')  , node_id=main_id)
            _.body_graph.create_element(node_path=Node_Path('body.footer'), node_id=footer_id)

            _.body_graph.add_child(body_root, header_id, position=0)
            _.body_graph.add_child(body_root, main_id  , position=1)
            _.body_graph.add_child(body_root, footer_id, position=2)

            children = _.get_body_children(body_root)

            assert len(children) == 3
            assert children == [header_id, main_id, footer_id]

    def test_get_body_children__empty(self):                                    # Test getting children when none exist
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id

            children = _.get_body_children(body_root)

            assert children == []

    def test_get_body_children__nested(self):                                   # Test getting children of nested element
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())
            p_id      = Node_Id(Obj_Id())
            span_id   = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div')     , node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.p')   , node_id=p_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.span'), node_id=span_id)

            _.body_graph.add_child(body_root, div_id , position=0)
            _.body_graph.add_child(div_id   , p_id   , position=0)
            _.body_graph.add_child(div_id   , span_id, position=1)

            div_children = _.get_body_children(div_id)

            assert len(div_children) == 2
            assert div_children == [p_id, span_id]

    # ═══════════════════════════════════════════════════════════════════════════
    # get_head_children Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_head_children__single(self):                                   # Test getting single head child
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta'), node_id=meta_id)
            _.head_graph.add_child(head_root, meta_id, position=0)

            children = _.get_head_children(head_root)

            assert children == [meta_id]

    def test_get_head_children__multiple(self):                                 # Test getting multiple head children
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())
            title_id  = Node_Id(Obj_Id())
            link_id   = Node_Id(Obj_Id())
            style_id  = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta') , node_id=meta_id)
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.create_element(node_path=Node_Path('head.link') , node_id=link_id)
            _.head_graph.create_element(node_path=Node_Path('head.style'), node_id=style_id)

            _.head_graph.add_child(head_root, meta_id , position=0)
            _.head_graph.add_child(head_root, title_id, position=1)
            _.head_graph.add_child(head_root, link_id , position=2)
            _.head_graph.add_child(head_root, style_id, position=3)

            children = _.get_head_children(head_root)

            assert len(children) == 4
            assert children == [meta_id, title_id, link_id, style_id]

    def test_get_head_children__empty(self):                                    # Test getting children when none exist
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id

            children = _.get_head_children(head_root)

            assert children == []

    # ═══════════════════════════════════════════════════════════════════════════
    # walk_body Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_walk_body__default_root(self):                                     # Test walk_body with default root
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            _.attrs_graph.register_element(body_root, 'body')

            result = _.walk_body()

            assert len(result) == 1
            assert result[0]['tag'] == 'body'

    def test_walk_body__with_children(self):                                    # Test walk_body with children
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())
            p_id      = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div')  , node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.p'), node_id=p_id)
            _.body_graph.add_child(body_root, div_id, position=0)
            _.body_graph.add_child(div_id   , p_id  , position=0)

            _.attrs_graph.register_element(body_root, 'body')
            _.attrs_graph.register_element(div_id   , 'div')
            _.attrs_graph.register_element(p_id     , 'p')

            result = _.walk_body()

            assert len(result) == 3
            tags = [item['tag'] for item in result]
            assert 'body' in tags
            assert 'div'  in tags
            assert 'p'    in tags

    def test_walk_body__from_specific_node(self):                               # Test walk_body from specific node
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            div_id    = Node_Id(Obj_Id())
            span_id   = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div')     , node_id=div_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.span'), node_id=span_id)
            _.body_graph.add_child(body_root, div_id , position=0)
            _.body_graph.add_child(div_id   , span_id, position=0)

            _.attrs_graph.register_element(div_id , 'div')
            _.attrs_graph.register_element(span_id, 'span')

            result = _.walk_body(div_id)                                        # Start from div, not body

            assert len(result) == 2
            tags = [item['tag'] for item in result]
            assert 'div'  in tags
            assert 'span' in tags
            assert 'body' not in tags

    def test_walk_body__deep_nesting(self):                                     # Test walk_body with deeply nested structure
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            level1_id = Node_Id(Obj_Id())
            level2_id = Node_Id(Obj_Id())
            level3_id = Node_Id(Obj_Id())
            level4_id = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div')          , node_id=level1_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.div')      , node_id=level2_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.div.div')  , node_id=level3_id)
            _.body_graph.create_element(node_path=Node_Path('body.div.div.div.p'), node_id=level4_id)

            _.body_graph.add_child(body_root, level1_id, position=0)
            _.body_graph.add_child(level1_id, level2_id, position=0)
            _.body_graph.add_child(level2_id, level3_id, position=0)
            _.body_graph.add_child(level3_id, level4_id, position=0)

            _.attrs_graph.register_element(body_root, 'body')
            _.attrs_graph.register_element(level1_id, 'div')
            _.attrs_graph.register_element(level2_id, 'div')
            _.attrs_graph.register_element(level3_id, 'div')
            _.attrs_graph.register_element(level4_id, 'p')

            result = _.walk_body()

            assert len(result) == 5                                             # body + 4 nested elements

    def test_walk_body__multiple_siblings(self):                                # Test walk_body with multiple siblings
        with Html_MGraph__Document().setup() as _:
            body_root = _.body_graph.root_id
            header_id = Node_Id(Obj_Id())
            main_id   = Node_Id(Obj_Id())
            footer_id = Node_Id(Obj_Id())
            p1_id     = Node_Id(Obj_Id())
            p2_id     = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.header'), node_id=header_id)
            _.body_graph.create_element(node_path=Node_Path('body.main')  , node_id=main_id)
            _.body_graph.create_element(node_path=Node_Path('body.footer'), node_id=footer_id)
            _.body_graph.create_element(node_path=Node_Path('body.main.p[0]'), node_id=p1_id)
            _.body_graph.create_element(node_path=Node_Path('body.main.p[1]'), node_id=p2_id)

            _.body_graph.add_child(body_root, header_id, position=0)
            _.body_graph.add_child(body_root, main_id  , position=1)
            _.body_graph.add_child(body_root, footer_id, position=2)
            _.body_graph.add_child(main_id  , p1_id    , position=0)
            _.body_graph.add_child(main_id  , p2_id    , position=1)

            _.attrs_graph.register_element(body_root, 'body')
            _.attrs_graph.register_element(header_id, 'header')
            _.attrs_graph.register_element(main_id  , 'main')
            _.attrs_graph.register_element(footer_id, 'footer')
            _.attrs_graph.register_element(p1_id    , 'p')
            _.attrs_graph.register_element(p2_id    , 'p')

            result = _.walk_body()

            assert len(result) == 6                                             # body, header, main, footer, 2 p's

    # ═══════════════════════════════════════════════════════════════════════════
    # walk_head Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_walk_head__default_root(self):                                     # Test walk_head with default root
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            _.attrs_graph.register_element(head_root, 'head')

            result = _.walk_head()

            assert len(result) == 1
            assert result[0]['tag'] == 'head'

    def test_walk_head__with_children(self):                                    # Test walk_head with children
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())
            title_id  = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta') , node_id=meta_id)
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.add_child(head_root, meta_id , position=0)
            _.head_graph.add_child(head_root, title_id, position=1)

            _.attrs_graph.register_element(head_root, 'head')
            _.attrs_graph.register_element(meta_id  , 'meta')
            _.attrs_graph.register_element(title_id , 'title')

            result = _.walk_head()

            assert len(result) == 3
            tags = [item['tag'] for item in result]
            assert 'head'  in tags
            assert 'meta'  in tags
            assert 'title' in tags

    def test_walk_head__from_specific_node(self):                               # Test walk_head from specific node
        with Html_MGraph__Document().setup() as _:
            head_root = _.head_graph.root_id
            meta_id   = Node_Id(Obj_Id())
            title_id  = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.meta') , node_id=meta_id)
            _.head_graph.create_element(node_path=Node_Path('head.title'), node_id=title_id)
            _.head_graph.add_child(head_root, meta_id , position=0)
            _.head_graph.add_child(head_root, title_id, position=1)

            _.attrs_graph.register_element(title_id, 'title')

            result = _.walk_head(title_id)                                      # Start from title

            assert len(result) == 1
            assert result[0]['tag'] == 'title'

    def test_walk_head__with_noscript(self):                                    # Test walk_head with nested noscript
        with Html_MGraph__Document().setup() as _:
            head_root   = _.head_graph.root_id
            noscript_id = Node_Id(Obj_Id())
            link_id     = Node_Id(Obj_Id())

            _.head_graph.create_element(node_path=Node_Path('head.noscript')     , node_id=noscript_id)
            _.head_graph.create_element(node_path=Node_Path('head.noscript.link'), node_id=link_id)
            _.head_graph.add_child(head_root  , noscript_id, position=0)
            _.head_graph.add_child(noscript_id, link_id    , position=0)

            _.attrs_graph.register_element(head_root  , 'head')
            _.attrs_graph.register_element(noscript_id, 'noscript')
            _.attrs_graph.register_element(link_id    , 'link')

            result = _.walk_head()

            assert len(result) == 3
            tags = [item['tag'] for item in result]
            assert 'head'     in tags
            assert 'noscript' in tags
            assert 'link'     in tags

    # ═══════════════════════════════════════════════════════════════════════════
    # to_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_to_json__structure(self):                                          # Test to_json returns expected structure
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

    def test_to_json__with_content(self):                                       # Test to_json with populated graphs
        with Html_MGraph__Document().setup() as _:
            div_id    = Node_Id(Obj_Id())
            script_id = Node_Id(Obj_Id())
            style_id  = Node_Id(Obj_Id())

            _.body_graph.create_element(node_path=Node_Path('body.div'), node_id=div_id)
            _.body_graph.add_child(_.body_graph.root_id, div_id, position=0)

            _.attrs_graph.register_element(div_id   , 'div')
            _.attrs_graph.register_element(script_id, 'script')
            _.attrs_graph.register_element(style_id , 'style')
            _.attrs_graph.add_attribute(div_id, 'class', 'container', position=0)

            _.scripts_graph.register_script(script_id, content="alert('hi');")
            _.styles_graph.register_style(style_id, content=".test {}")

            json_data = _.to_json()

            assert 'document'   in json_data
            assert 'body'       in json_data
            assert 'attributes' in json_data
            assert 'scripts'    in json_data
            assert 'styles'     in json_data

    def test_to_json__empty_graphs(self):                                       # Test to_json with minimal setup
        with Html_MGraph__Document().setup() as _:
            json_data = _.to_json()

            assert json_data['document']   is not None                          # Should still have document data
            assert json_data['head']       is not None
            assert json_data['body']       is not None
            assert json_data['attributes'] is not None
            assert json_data['scripts']    is not None
            assert json_data['styles']     is not None

    def test_to_json__serializable(self):                                       # Test to_json output is JSON serializable
        import json

        with Html_MGraph__Document().setup() as _:
            div_id = Node_Id(Obj_Id())
            _.attrs_graph.register_element(div_id, 'div')
            _.attrs_graph.add_attribute(div_id, 'id', 'test', position=0)

            json_data = _.to_json()

            json_string = json.dumps(json_data)                                 # Should not raise
            assert type(json_string) is str
            assert len(json_string) > 0