# ═══════════════════════════════════════════════════════════════════════════════
# IFD Dependency Extractor - Extract dependencies using Html_MGraph
# Leverages Html_MGraph's scripts_graph and styles_graph for clean extraction
# ═══════════════════════════════════════════════════════════════════════════════

import os
import re
from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                             import type_safe
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Resource_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__File_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_UInt__Load_Order


VERSION_PATTERN = re.compile(r'(v\d+\.\d+\.\d+)')                                          # Matches v0.2.0, v0.2.10, v1.0.0


class IFD_Dependency_Extractor(Type_Safe):                                                 # Extract deps from HTML using Html_MGraph
    seen_logical_names : List[Safe_Str__Logical_Name]                                      # Track seen names for base/surgical classification

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Extraction Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_from_html(self                                     ,                       # Extract all external dependencies
                          html_content : str                  ,                       # Raw HTML content
                          html_path    : Safe_Str__File__Path      ,                       # Path to HTML file
                          base_path    : Safe_Str__File__Path                              # Base path for resolution
                     ) -> List[Schema__IFD_Dependency]:
        html_mgraph  = Html_MGraph.from_html(html_content)
        dependencies = []
        load_order   = Safe_UInt__Load_Order(0)

        # Extract external stylesheets via styles_graph (CSS loads first in HTML)
        css_deps, load_order = self.extract_css_dependencies(html_mgraph, html_path, base_path, load_order)
        dependencies.extend(css_deps)

        # Extract external scripts via scripts_graph
        js_deps, load_order = self.extract_js_dependencies(html_mgraph, html_path, base_path, load_order)
        dependencies.extend(js_deps)

        return dependencies

    # ═══════════════════════════════════════════════════════════════════════════
    # CSS Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_css_dependencies(self                                        ,             # Extract external stylesheets
                                 html_mgraph : Html_MGraph                   ,
                                 html_path   : Safe_Str__File__Path          ,
                                 base_path   : Safe_Str__File__Path          ,
                                 load_order  : Safe_UInt__Load_Order
                            ) -> tuple:                                                    # Returns (deps, new_load_order)
        dependencies = []

        for style_id in html_mgraph.styles_graph.get_all_styles():
            if html_mgraph.styles_graph.is_external_style(style_id):
                href = html_mgraph.get_attribute(style_id, 'href')
                if href:
                    dep = self.create_dependency(original_path  = href                    ,
                                                 html_path      = html_path                         ,
                                                 base_path      = base_path                         ,
                                                 resource_type  = Safe_Str__Resource_Type('css')    ,
                                                 load_order     = load_order                        )
                    if dep:
                        dependencies.append(dep)
                        load_order = Safe_UInt__Load_Order(int(load_order) + 1)

        return dependencies, load_order

    # ═══════════════════════════════════════════════════════════════════════════
    # JS Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_js_dependencies(self                                         ,             # Extract external scripts
                                html_mgraph : Html_MGraph                    ,
                                html_path   : Safe_Str__File__Path           ,
                                base_path   : Safe_Str__File__Path           ,
                                load_order  : Safe_UInt__Load_Order
                           ) -> tuple:                                                     # Returns (deps, new_load_order)
        dependencies = []

        for script_id in html_mgraph.scripts_graph.get_all_scripts():
            if html_mgraph.scripts_graph.is_external_script(script_id):
                src = html_mgraph.get_attribute(script_id, 'src')
                if src:
                    dep = self.create_dependency(original_path  = src                               ,
                                                 html_path      = html_path                         ,
                                                 base_path      = base_path                         ,
                                                 resource_type  = Safe_Str__Resource_Type('js')     ,
                                                 load_order     = load_order                        )
                    if dep:
                        dependencies.append(dep)
                        load_order = Safe_UInt__Load_Order(int(load_order) + 1)

        return dependencies, load_order

    # ═══════════════════════════════════════════════════════════════════════════
    # Dependency Creation
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def create_dependency(self                                     ,                       # Create dependency from path
                          original_path : Safe_Str__File__Path     ,
                          html_path     : Safe_Str__File__Path     ,
                          base_path     : Safe_Str__File__Path     ,
                          resource_type : Safe_Str__Resource_Type  ,
                          load_order    : Safe_UInt__Load_Order
                     ) -> Schema__IFD_Dependency:
        version = self.extract_version(original_path)
        if not version:                                                                    # Skip non-versioned paths (CDN, etc.)
            return None

        resolved     = self.resolve_path(original_path, html_path, base_path)
        logical_name = self.extract_logical_name(original_path)
        file_type    = self.classify_file_type(logical_name)

        return Schema__IFD_Dependency(original_path  = Safe_Str__File__Path(str(original_path)),
                                      resolved_path  = resolved                                ,
                                      source_version = version                                 ,
                                      resource_type  = resource_type                           ,
                                      file_type      = file_type                               ,
                                      logical_name   = logical_name                            ,
                                      load_order     = load_order                              )

    # ═══════════════════════════════════════════════════════════════════════════
    # Path Resolution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def resolve_path(self                                          ,                       # Resolve relative path to absolute
                     original_path : Safe_Str__File__Path                      ,
                     html_path     : Safe_Str__File__Path          ,
                     base_path     : Safe_Str__File__Path
                ) -> Safe_Str__File__Path:
        path_str = str(original_path)

        if path_str.startswith('/'):                                                       # Absolute path (web root)
            return Safe_Str__File__Path(path_str)

        # Relative path - resolve from HTML file's directory
        html_dir   = os.path.dirname(str(html_path))
        combined   = os.path.join(str(base_path), html_dir, path_str)
        normalized = os.path.normpath(combined)

        return Safe_Str__File__Path(normalized)

    # ═══════════════════════════════════════════════════════════════════════════
    # Version Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_version(self, path: Safe_Str__File__Path) -> Safe_Str__IFD_Version:                    # Extract vN.N.N from path
        path_str = str(path)
        match    = VERSION_PATTERN.search(path_str)

        if match:
            return Safe_Str__IFD_Version(match.group(1))
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Logical Name Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_logical_name(self, path: Safe_Str__File__Path) -> Safe_Str__Logical_Name:              # Extract logical name from path
        path_str = str(path)

        # Remove version prefix: ../v0.2.0/js/api-client.js → js/api-client.js
        match = re.search(r'v\d+\.\d+\.\d+/(.+)$', path_str)
        if match:
            relative = match.group(1)
            # Remove extension
            if relative.endswith('.js'):
                relative = relative[:-3]
            elif relative.endswith('.css'):
                relative = relative[:-4]
            return Safe_Str__Logical_Name(relative)

        return Safe_Str__Logical_Name(path_str)

    # ═══════════════════════════════════════════════════════════════════════════
    # File Type Classification
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def classify_file_type(self                                    ,                       # Classify as base or surgical
                           logical_name: Safe_Str__Logical_Name
                      ) -> Safe_Str__File_Type:
        if logical_name in self.seen_logical_names:
            return Safe_Str__File_Type('surgical')                                         # Already seen = surgical override

        self.seen_logical_names.append(logical_name)
        return Safe_Str__File_Type('base')                                                 # First occurrence = base

    # ═══════════════════════════════════════════════════════════════════════════
    # Reset State
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def reset_seen_names(self) -> 'IFD_Dependency_Extractor':                              # Reset tracking for new extraction
        self.seen_logical_names = []
        return self
