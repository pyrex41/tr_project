# PRD: Frontend Application
## Know Your Judge - Expert Witness Analysis

**Version:** 1.0  
**Date:** November 14, 2025  
**Owner:** Engineering Team  
**Timeline:** 3 hours (POC phase)

---

## 1. Overview

### 1.1 Purpose
Build an Elm-based web application that provides litigators with intuitive access to Judge Boyle's expert witness ruling patterns through interactive dashboards, powerful search, and detailed order analysis views.

### 1.2 Success Criteria
- ✅ Professional, Westlaw-style UI (clean, citation-rich, research-focused)
- ✅ Sub-second page load times for all views
- ✅ Intuitive navigation requiring no user training
- ✅ Responsive search with real-time feedback
- ✅ Accessible design (WCAG 2.1 AA compliance)
- ✅ Works in Chrome, Firefox, Safari (latest versions)

### 1.3 Technology Stack
- **Language:** Elm 0.19.1
- **Build Tool:** Vite 5.0+ with vite-plugin-elm
- **Styling:** Tailwind CSS 3.3+ (via CDN)
- **HTTP:** Elm's built-in Http module
- **Routing:** elm/url + elm/browser for SPA navigation
- **No external chart library needed** - Use CSS/SVG for simple visualizations

### 1.4 Design Principles
- **Research-First**: Dense information, scannable layouts
- **Citation-Heavy**: Westlaw-style case citations everywhere
- **Professional**: Blues, clean typography, serious tone
- **Fast**: Instant feedback, optimistic UI updates
- **Focused**: No feature bloat—shipping over polish

---

## 2. Architecture

### 2.1 Project Structure
```
frontend/
├── src/
│   ├── Main.elm                 # Entry point, routing
│   ├── Types.elm                # Shared types/models
│   ├── Api.elm                  # HTTP requests to backend
│   ├── Components/
│   │   ├── Layout.elm           # Header, footer, navigation
│   │   ├── SearchBar.elm        # Unified search component
│   │   ├── OrderCard.elm        # Order preview card
│   │   ├── StatCard.elm         # Dashboard stat cards
│   │   ├── Chart.elm            # Simple SVG charts
│   │   ├── QuoteCard.elm        # Copyable quote display
│   │   └── Modal.elm            # Full-text modal
│   └── Pages/
│       ├── Dashboard.elm        # Stats overview + insights
│       ├── Search.elm           # Search results page
│       ├── OrderDetail.elm      # Full order analysis view
│       └── NotFound.elm         # 404 page
├── public/
│   ├── index.html
│   └── favicon.ico
├── vite.config.js               # Vite + proxy config
├── elm.json                     # Elm dependencies
├── package.json                 # Node dependencies
└── README.md
```

### 2.2 Elm Architecture (TEA)
```elm
-- Main.elm
module Main exposing (main)

import Browser
import Browser.Navigation as Nav
import Html exposing (..)
import Pages.Dashboard as Dashboard
import Pages.Search as Search
import Pages.OrderDetail as OrderDetail
import Pages.NotFound as NotFound
import Types exposing (..)
import Url exposing (Url)
import Url.Parser as Parser exposing (Parser, (</>), int, s, string)

-- MODEL

type Model
    = DashboardModel Dashboard.Model
    | SearchModel Search.Model
    | OrderDetailModel OrderDetail.Model
    | NotFoundModel

type alias Flags =
    { apiBaseUrl : String }

-- INIT

init : Flags -> Url -> Nav.Key -> ( Model, Cmd Msg )
init flags url key =
    let
        route = parseUrl url
    in
    case route of
        DashboardRoute ->
            Dashboard.init flags.apiBaseUrl
                |> mapInit DashboardModel DashboardMsg
        
        SearchRoute query ->
            Search.init flags.apiBaseUrl query
                |> mapInit SearchModel SearchMsg
        
        OrderDetailRoute orderId ->
            OrderDetail.init flags.apiBaseUrl orderId
                |> mapInit OrderDetailModel OrderDetailMsg
        
        NotFoundRoute ->
            ( NotFoundModel, Cmd.none )

-- UPDATE

type Msg
    = UrlChanged Url
    | LinkClicked Browser.UrlRequest
    | DashboardMsg Dashboard.Msg
    | SearchMsg Search.Msg
    | OrderDetailMsg OrderDetail.Msg

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case ( msg, model ) of
        ( UrlChanged url, _ ) ->
            init flags url navKey  -- Re-route
        
        ( DashboardMsg subMsg, DashboardModel subModel ) ->
            Dashboard.update subMsg subModel
                |> mapUpdate DashboardModel DashboardMsg
        
        ( SearchMsg subMsg, SearchModel subModel ) ->
            Search.update subMsg subModel
                |> mapUpdate SearchModel SearchMsg
        
        ( OrderDetailMsg subMsg, OrderDetailModel subModel ) ->
            OrderDetail.update subMsg subModel
                |> mapUpdate OrderDetailModel OrderDetailMsg
        
        _ ->
            ( model, Cmd.none )

-- VIEW

view : Model -> Browser.Document Msg
view model =
    { title = "Know Your Judge - Expert Witness Analysis"
    , body =
        [ div [ class "app-container" ]
            [ viewHeader
            , case model of
                DashboardModel subModel ->
                    Html.map DashboardMsg (Dashboard.view subModel)
                
                SearchModel subModel ->
                    Html.map SearchMsg (Search.view subModel)
                
                OrderDetailModel subModel ->
                    Html.map OrderDetailMsg (OrderDetail.view subModel)
                
                NotFoundModel ->
                    NotFound.view
            ]
        ]
    }

-- ROUTING

type Route
    = DashboardRoute
    | SearchRoute (Maybe String)
    | OrderDetailRoute Int
    | NotFoundRoute

routeParser : Parser (Route -> a) a
routeParser =
    Parser.oneOf
        [ Parser.map DashboardRoute Parser.top
        , Parser.map SearchRoute (s "search" <?> Query.string "q")
        , Parser.map OrderDetailRoute (s "orders" </> int)
        ]

parseUrl : Url -> Route
parseUrl url =
    Parser.parse routeParser url
        |> Maybe.withDefault NotFoundRoute
```

---

## 3. User Interface Design

### 3.1 Design System

**Color Palette:**
```css
:root {
    /* Primary colors */
    --primary-blue: #0066cc;
    --dark-blue: #003d7a;
    --light-blue: #e6f2ff;
    
    /* Status colors */
    --success-green: #28a745;
    --warning-yellow: #ffc107;
    --danger-red: #dc3545;
    
    /* Neutrals */
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-muted: #adb5bd;
    --bg-white: #ffffff;
    --bg-gray: #f8f9fa;
    --bg-light: #e9ecef;
    --border-gray: #dee2e6;
}
```

**Typography:**
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: var(--text-primary);
}

h1 { font-size: 2rem; font-weight: 600; margin-bottom: 1rem; }
h2 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.75rem; }
h3 { font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem; }

.case-name {
    font-family: Georgia, serif;
    font-style: italic;
    color: var(--primary-blue);
}

.legal-citation {
    font-size: 0.9rem;
    color: var(--text-secondary);
}
```

### 3.2 Component Library

**Button Styles:**
```css
.btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary-blue);
    color: white;
}

.btn-secondary {
    background: var(--bg-gray);
    color: var(--text-primary);
}
```

---

## 4. Page Specifications

### 4.1 Dashboard Page

**URL:** `/`

**Purpose:** High-level overview with quick insights and search.

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ HEADER: Know Your Judge                                 │
├─────────────────────────────────────────────────────────┤
│ Judge Jane J. Boyle - Expert Witness Patterns           │
│ Northern District of Texas                               │
│                                                          │
│ [Search: _______________] [Keyword ▼] [Semantic] [Go]   │
├─────────────────────────────────────────────────────────┤
│ STAT CARDS:                                              │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │ 19 Cases │ │ 63% Grant│ │ Medical  │ │ 8 Orders │   │
│ │ Analyzed │ │   Rate   │ │ Top Type │ │ Partial  │   │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│ 🧠 AI-DISCOVERED PATTERNS                               │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ⚠️  Peer-reviewed methodology required (80%)       │  │
│ │     Evidence: Case 1, Case 3, Case 7              │  │
│ └────────────────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ✓  Fire investigators using NFPA rarely excluded  │  │
│ │     Evidence: Case 8, Case 12                      │  │
│ └────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ RULING BREAKDOWN           EXPERT TYPES                 │
│ ┌──────────────┐          ┌──────────────┐             │
│ │              │          │ Medical: 42% │             │
│ │  Pie Chart   │          │ Financial: 21%│            │
│ │              │          │ Fire: 11%    │             │
│ └──────────────┘          │ Other: 26%   │             │
│                            └──────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Elm Implementation:**
```elm
-- Pages/Dashboard.elm
module Pages.Dashboard exposing (Model, Msg, init, update, view)

import Api
import Components.StatCard as StatCard
import Components.Chart as Chart
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onInput, onClick)
import Http
import Types exposing (..)

-- MODEL

type alias Model =
    { apiBaseUrl : String
    , stats : RemoteData Stats
    , insights : RemoteData (List Insight)
    , searchQuery : String
    , searchType : SearchType
    }

type RemoteData a
    = NotAsked
    | Loading
    | Failure String
    | Success a

type SearchType = Keyword | Semantic

-- INIT

init : String -> ( Model, Cmd Msg )
init apiBaseUrl =
    ( { apiBaseUrl = apiBaseUrl
      , stats = Loading
      , insights = Loading
      , searchQuery = ""
      , searchType = Keyword
      }
    , Cmd.batch
        [ Api.getStats apiBaseUrl StatsReceived
        , Api.getInsights apiBaseUrl InsightsReceived
        ]
    )

-- UPDATE

type Msg
    = StatsReceived (Result Http.Error Stats)
    | InsightsReceived (Result Http.Error (List Insight))
    | SearchQueryChanged String
    | SearchTypeToggled SearchType
    | QuickSearchSubmitted

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        StatsReceived (Ok stats) ->
            ( { model | stats = Success stats }, Cmd.none )
        
        StatsReceived (Err err) ->
            ( { model | stats = Failure (httpErrorToString err) }, Cmd.none )
        
        InsightsReceived (Ok insights) ->
            ( { model | insights = Success insights }, Cmd.none )
        
        InsightsReceived (Err err) ->
            ( { model | insights = Failure (httpErrorToString err) }, Cmd.none )
        
        SearchQueryChanged query ->
            ( { model | searchQuery = query }, Cmd.none )
        
        SearchTypeToggled searchType ->
            ( { model | searchType = searchType }, Cmd.none )
        
        QuickSearchSubmitted ->
            ( model
            , Nav.pushUrl model.navKey ("/search?q=" ++ model.searchQuery)
            )

-- VIEW

view : Model -> Html Msg
view model =
    div [ class "dashboard-page max-w-6xl mx-auto p-6" ]
        [ viewPageHeader
        , viewQuickSearch model.searchQuery model.searchType
        , viewStats model.stats
        , viewInsights model.insights
        , viewCharts model.stats
        ]

viewPageHeader : Html Msg
viewPageHeader =
    div [ class "page-header mb-8" ]
        [ h1 [ class "text-3xl font-bold text-gray-900" ]
            [ text "Judge Jane J. Boyle - Expert Witness Patterns" ]
        , p [ class "text-gray-600 mt-2" ]
            [ text "Northern District of Texas" ]
        ]

viewQuickSearch : String -> SearchType -> Html Msg
viewQuickSearch query searchType =
    div [ class "quick-search bg-white p-6 rounded-lg shadow-sm mb-8" ]
        [ div [ class "flex gap-3" ]
            [ input
                [ class "flex-1 px-4 py-2 border border-gray-300 rounded"
                , placeholder "Search orders (e.g., 'daubert methodology')"
                , value query
                , onInput SearchQueryChanged
                ]
                []
            , select
                [ class "px-4 py-2 border border-gray-300 rounded"
                , onInput (\val -> 
                    SearchTypeToggled (if val == "semantic" then Semantic else Keyword))
                ]
                [ option [ value "keyword", selected (searchType == Keyword) ] 
                    [ text "Keyword" ]
                , option [ value "semantic", selected (searchType == Semantic) ] 
                    [ text "Semantic" ]
                ]
            , button
                [ class "btn-primary px-6 py-2 rounded"
                , onClick QuickSearchSubmitted
                ]
                [ text "Search" ]
            ]
        ]

viewStats : RemoteData Stats -> Html Msg
viewStats remoteStats =
    case remoteStats of
        Loading ->
            div [ class "text-center py-8" ] [ text "Loading statistics..." ]
        
        Failure err ->
            div [ class "bg-red-50 text-red-800 p-4 rounded" ] 
                [ text ("Error: " ++ err) ]
        
        Success stats ->
            div [ class "stats-grid grid grid-cols-4 gap-4 mb-8" ]
                [ StatCard.view "Total Cases" (String.fromInt stats.totalOrders) "📋"
                , StatCard.view "Grant Rate" 
                    (String.fromInt (round (stats.grantRate * 100)) ++ "%") "⚖️"
                , StatCard.view "Top Expert Type" 
                    (stats.topExpertType |> Maybe.withDefault "N/A") "👨‍⚕️"
                , StatCard.view "Partial Rulings" 
                    (String.fromInt stats.partialCount) "⚠️"
                ]
        
        NotAsked ->
            text ""

viewInsights : RemoteData (List Insight) -> Html Msg
viewInsights remoteInsights =
    case remoteInsights of
        Success insights ->
            div [ class "insights-section mb-8" ]
                [ h2 [ class "text-2xl font-semibold mb-4 flex items-center gap-2" ]
                    [ text "🧠"
                    , text "AI-Discovered Patterns"
                    ]
                , p [ class "text-gray-600 mb-4" ]
                    [ text "Deep analysis of all 19 orders reveals these judicial tendencies:" ]
                , div [ class "space-y-3" ]
                    (List.map viewInsightCard insights)
                ]
        
        Loading ->
            div [ class "text-center py-4" ] [ text "Analyzing patterns..." ]
        
        _ ->
            text ""

viewInsightCard : Insight -> Html Msg
viewInsightCard insight =
    div [ class ("insight-card p-4 rounded-lg border-l-4 " ++ insightColorClass insight.type_) ]
        [ div [ class "flex justify-between items-start mb-2" ]
            [ span [ class "text-xl" ] [ text (insightIcon insight.type_) ]
            , span [ class "text-sm text-gray-500" ] 
                [ text (String.fromInt insight.confidence ++ "% confidence") ]
            ]
        , p [ class "text-gray-900 mb-2" ] [ text insight.description ]
        , div [ class "text-sm text-gray-600" ]
            [ text "Evidence: "
            , span [] (List.intersperse (text ", ") 
                (List.map viewEvidenceLink insight.orderIds))
            ]
        ]

viewEvidenceLink : Int -> Html Msg
viewEvidenceLink orderId =
    a [ class "text-blue-600 hover:underline"
      , href ("/orders/" ++ String.fromInt orderId)
      ]
      [ text ("Case " ++ String.fromInt orderId) ]

insightIcon : String -> String
insightIcon type_ =
    case type_ of
        "warning" -> "⚠️"
        "success" -> "✓"
        "info" -> "ℹ️"
        _ -> "•"

insightColorClass : String -> String
insightColorClass type_ =
    case type_ of
        "warning" -> "border-yellow-400 bg-yellow-50"
        "success" -> "border-green-400 bg-green-50"
        "info" -> "border-blue-400 bg-blue-50"
        _ -> "border-gray-400 bg-gray-50"

viewCharts : RemoteData Stats -> Html Msg
viewCharts remoteStats =
    case remoteStats of
        Success stats ->
            div [ class "charts-section grid grid-cols-2 gap-6" ]
                [ div [ class "bg-white p-6 rounded-lg shadow-sm" ]
                    [ h3 [ class "text-lg font-semibold mb-4" ] 
                        [ text "Ruling Breakdown" ]
                    , Chart.pieChart stats.rulings
                    ]
                , div [ class "bg-white p-6 rounded-lg shadow-sm" ]
                    [ h3 [ class "text-lg font-semibold mb-4" ] 
                        [ text "Expert Types" ]
                    , Chart.barChart stats.expertTypes
                    ]
                ]
        
        _ ->
            text ""
```

### 4.2 Search Page

**URL:** `/search?q=daubert`

**Purpose:** Display keyword or semantic search results.

**Elm Implementation:**
```elm
-- Pages/Search.elm
module Pages.Search exposing (Model, Msg, init, update, view)

import Api
import Components.OrderCard as OrderCard
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onInput, onClick)
import Http
import Types exposing (..)

-- MODEL

type alias Model =
    { apiBaseUrl : String
    , query : String
    , searchType : SearchType
    , results : RemoteData (List SearchResult)
    , filters : Filters
    }

type alias Filters =
    { rulingType : Maybe String
    , expertField : Maybe String
    }

-- INIT

init : String -> Maybe String -> ( Model, Cmd Msg )
init apiBaseUrl maybeQuery =
    let
        query = maybeQuery |> Maybe.withDefault ""
        
        model =
            { apiBaseUrl = apiBaseUrl
            , query = query
            , searchType = Keyword
            , results = Loading
            , filters = { rulingType = Nothing, expertField = Nothing }
            }
    in
    if String.isEmpty query then
        ( { model | results = NotAsked }, Cmd.none )
    else
        ( model, performSearch model )

-- UPDATE

type Msg
    = QueryChanged String
    | SearchTypeToggled SearchType
    | SearchSubmitted
    | ResultsReceived (Result Http.Error (List SearchResult))
    | FilterChanged Filters

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        QueryChanged query ->
            ( { model | query = query }, Cmd.none )
        
        SearchTypeToggled searchType ->
            ( { model | searchType = searchType }
            , performSearch { model | searchType = searchType }
            )
        
        SearchSubmitted ->
            ( { model | results = Loading }
            , performSearch model
            )
        
        ResultsReceived (Ok results) ->
            ( { model | results = Success results }, Cmd.none )
        
        ResultsReceived (Err err) ->
            ( { model | results = Failure (httpErrorToString err) }, Cmd.none )
        
        FilterChanged filters ->
            ( { model | filters = filters }, Cmd.none )

performSearch : Model -> Cmd Msg
performSearch model =
    case model.searchType of
        Keyword ->
            Api.keywordSearch model.apiBaseUrl model.query ResultsReceived
        
        Semantic ->
            Api.semanticSearch model.apiBaseUrl model.query ResultsReceived

-- VIEW

view : Model -> Html Msg
view model =
    div [ class "search-page max-w-6xl mx-auto p-6" ]
        [ viewSearchBar model
        , viewResults model.results
        ]

viewSearchBar : Model -> Html Msg
viewSearchBar model =
    div [ class "search-bar bg-white p-6 rounded-lg shadow-sm mb-6" ]
        [ div [ class "flex gap-3" ]
            [ input
                [ class "flex-1 px-4 py-2 border border-gray-300 rounded"
                , placeholder "Search expert witness orders..."
                , value model.query
                , onInput QueryChanged
                ]
                []
            , div [ class "flex gap-2" ]
                [ button
                    [ class (if model.searchType == Keyword then "btn-primary" else "btn-secondary")
                    , onClick (SearchTypeToggled Keyword)
                    ]
                    [ text "Keyword" ]
                , button
                    [ class (if model.searchType == Semantic then "btn-primary" else "btn-secondary")
                    , onClick (SearchTypeToggled Semantic)
                    ]
                    [ text "Semantic" ]
                ]
            , button
                [ class "btn-primary px-6 py-2 rounded"
                , onClick SearchSubmitted
                ]
                [ text "Search" ]
            ]
        ]

viewResults : RemoteData (List SearchResult) -> Html Msg
viewResults remoteResults =
    case remoteResults of
        NotAsked ->
            div [ class "text-center py-12 text-gray-500" ]
                [ text "Enter a search query to begin" ]
        
        Loading ->
            div [ class "text-center py-12" ]
                [ div [ class "animate-spin text-4xl" ] [ text "⟳" ]
                , p [ class "mt-4 text-gray-600" ] [ text "Searching..." ]
                ]
        
        Failure err ->
            div [ class "bg-red-50 text-red-800 p-6 rounded" ]
                [ h3 [ class "font-semibold mb-2" ] [ text "Search Error" ]
                , p [] [ text err ]
                ]
        
        Success results ->
            if List.isEmpty results then
                div [ class "text-center py-12 text-gray-500" ]
                    [ text "No results found" ]
            else
                div []
                    [ div [ class "mb-4 text-gray-600" ]
                        [ text (String.fromInt (List.length results) ++ " results found") ]
                    , div [ class "space-y-4" ]
                        (List.map viewResultCard results)
                    ]

viewResultCard : SearchResult -> Html Msg
viewResultCard result =
    div [ class "result-card bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition" ]
        [ div [ class "flex justify-between items-start mb-3" ]
            [ a [ class "case-name text-xl hover:underline"
                , href ("/orders/" ++ String.fromInt result.orderId)
                ]
                [ text result.caseName ]
            , span [ class ("ruling-badge px-3 py-1 rounded text-sm " ++ rulingBadgeClass result.rulingType) ]
                [ text (formatRuling result.rulingType) ]
            ]
        , div [ class "text-sm text-gray-600 mb-3" ]
            [ text ("Expert: " ++ result.expertName ++ " (" ++ result.expertField ++ ")") ]
        , div [ class "snippet text-gray-700 mb-3" ]
            [ renderHtmlSnippet result.snippet ]  -- Contains <mark> tags
        , case result.analysisInsight of
            Just insight ->
                div [ class "bg-blue-50 p-3 rounded mb-3" ]
                    [ strong [ class "text-blue-900" ] [ text "Strategic Insight: " ]
                    , span [ class "text-blue-800" ] [ text insight ]
                    ]
            Nothing ->
                text ""
        , a [ class "text-blue-600 hover:underline font-medium"
            , href ("/orders/" ++ String.fromInt result.orderId)
            ]
            [ text "View Full Analysis →" ]
        ]

rulingBadgeClass : String -> String
rulingBadgeClass ruling =
    case ruling of
        "granted" -> "bg-red-100 text-red-800"
        "denied" -> "bg-green-100 text-green-800"
        "partial" -> "bg-yellow-100 text-yellow-800"
        _ -> "bg-gray-100 text-gray-800"

formatRuling : String -> String
formatRuling ruling =
    case ruling of
        "granted" -> "⚠️ Excluded"
        "denied" -> "✓ Allowed"
        "partial" -> "⚡ Limited"
        _ -> ruling
```

### 4.3 Order Detail Page

**URL:** `/orders/1`

**Purpose:** Full order with tabs for overview, analysis, citations.

**Elm Implementation:**
```elm
-- Pages/OrderDetail.elm
module Pages.OrderDetail exposing (Model, Msg, init, update, view)

import Api
import Components.QuoteCard as QuoteCard
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Http
import Types exposing (..)

-- MODEL

type alias Model =
    { apiBaseUrl : String
    , orderId : Int
    , order : RemoteData OrderDetail
    , activeTab : Tab
    }

type Tab
    = OverviewTab
    | FullTextTab
    | AnalysisTab
    | CitationsTab
    | QuotesTab

-- INIT

init : String -> Int -> ( Model, Cmd Msg )
init apiBaseUrl orderId =
    ( { apiBaseUrl = apiBaseUrl
      , orderId = orderId
      , order = Loading
      , activeTab = OverviewTab
      }
    , Api.getOrderDetail apiBaseUrl orderId OrderReceived
    )

-- UPDATE

type Msg
    = OrderReceived (Result Http.Error OrderDetail)
    | TabClicked Tab
    | CopyQuote String

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        OrderReceived (Ok order) ->
            ( { model | order = Success order }, Cmd.none )
        
        OrderReceived (Err err) ->
            ( { model | order = Failure (httpErrorToString err) }, Cmd.none )
        
        TabClicked tab ->
            ( { model | activeTab = tab }, Cmd.none )
        
        CopyQuote text ->
            ( model, copyToClipboard text )

-- VIEW

view : Model -> Html Msg
view model =
    div [ class "order-detail-page max-w-5xl mx-auto p-6" ]
        [ viewBackButton
        , case model.order of
            Loading ->
                viewLoading
            
            Failure err ->
                viewError err
            
            Success order ->
                viewOrderContent model.activeTab order
            
            NotAsked ->
                text ""
        ]

viewBackButton : Html Msg
viewBackButton =
    a [ class "inline-block mb-4 text-blue-600 hover:underline"
      , href "/search"
      ]
      [ text "← Back to Search" ]

viewOrderContent : Tab -> OrderDetail -> Html Msg
viewOrderContent activeTab order =
    div []
        [ viewOrderHeader order
        , viewTabs activeTab
        , viewTabContent activeTab order
        ]

viewOrderHeader : OrderDetail -> Html Msg
viewOrderHeader order =
    div [ class "order-header bg-white p-6 rounded-lg shadow-sm mb-6" ]
        [ h1 [ class "case-name text-3xl mb-2" ] [ text order.caseName ]
        , div [ class "text-gray-600" ]
            [ text (order.docketNumber ++ " | " ++ order.date) ]
        ]

viewTabs : Tab -> Html Msg
viewTabs activeTab =
    div [ class "tabs flex gap-2 mb-6 border-b border-gray-200" ]
        (List.map (viewTab activeTab)
            [ ( OverviewTab, "Overview" )
            , ( AnalysisTab, "Analysis" )
            , ( FullTextTab, "Full Text" )
            , ( CitationsTab, "Citations" )
            , ( QuotesTab, "Quotes" )
            ])

viewTab : Tab -> ( Tab, String ) -> Html Msg
viewTab activeTab ( tab, label ) =
    button
        [ class (if activeTab == tab then
                "px-4 py-2 border-b-2 border-blue-600 text-blue-600 font-medium"
              else
                "px-4 py-2 text-gray-600 hover:text-gray-900")
        , onClick (TabClicked tab)
        ]
        [ text label ]

viewTabContent : Tab -> OrderDetail -> Html Msg
viewTabContent activeTab order =
    case activeTab of
        OverviewTab ->
            viewOverviewTab order
        
        AnalysisTab ->
            viewAnalysisTab order.analysis
        
        FullTextTab ->
            viewFullTextTab order.fullText
        
        CitationsTab ->
            viewCitationsTab order.analysis.precedentAnalysis
        
        QuotesTab ->
            viewQuotesTab order.analysis.keyQuotes

viewOverviewTab : OrderDetail -> Html Msg
viewOverviewTab order =
    div [ class "overview-content bg-white p-6 rounded-lg shadow-sm" ]
        [ section [ class "mb-6" ]
            [ h2 [ class "text-2xl font-semibold mb-3" ] [ text "Executive Summary" ]
            , p [ class "text-lg text-gray-700" ] [ text order.analysis.executiveSummary ]
            ]
        , section [ class "mb-6" ]
            [ h2 [ class "text-2xl font-semibold mb-3" ] [ text "Strategic Implications" ]
            , div [ class "grid grid-cols-2 gap-6" ]
                [ div [ class "bg-green-50 p-4 rounded" ]
                    [ h3 [ class "font-semibold text-green-900 mb-2" ] 
                        [ text "✓ Winning Arguments" ]
                    , ul [ class "space-y-1" ]
                        (List.map viewStrategyItem order.analysis.strategicImplications.challengingSimilar)
                    ]
                , div [ class "bg-red-50 p-4 rounded" ]
                    [ h3 [ class "font-semibold text-red-900 mb-2" ] 
                        [ text "⚠️ Pitfalls to Avoid" ]
                    , ul [ class "space-y-1" ]
                        (List.map viewRiskItem order.analysis.riskFactors)
                    ]
                ]
            ]
        ]

viewAnalysisTab : Analysis -> Html Msg
viewAnalysisTab analysis =
    div [ class "analysis-content bg-white p-6 rounded-lg shadow-sm space-y-6" ]
        [ viewAnalysisSection "Legal Framework" analysis.legalFramework
        , viewAnalysisSection "Judge's Reasoning" analysis.reasoningAnalysis
        , viewAnalysisSection "Expert Evaluation" analysis.expertEvaluation
        , viewRecommendations analysis.recommendations
        ]

viewFullTextTab : String -> Html Msg
viewFullTextTab fullText =
    div [ class "full-text bg-white p-6 rounded-lg shadow-sm" ]
        [ pre [ class "whitespace-pre-wrap font-mono text-sm" ] [ text fullText ]
        ]

viewQuotesTab : List KeyQuote -> Html Msg
viewQuotesTab quotes =
    div [ class "quotes-content space-y-4" ]
        (List.map (QuoteCard.view CopyQuote) quotes)
```

---

## 5. API Integration

**File:** `Api.elm`

```elm
module Api exposing
    ( getStats
    , getInsights
    , keywordSearch
    , semanticSearch
    , getOrderDetail
    )

import Http
import Json.Decode as Decode
import Types exposing (..)

-- BASE URL

baseUrl : String -> String
baseUrl apiBaseUrl =
    apiBaseUrl ++ "/api"

-- GET /api/stats

getStats : String -> (Result Http.Error Stats -> msg) -> Cmd msg
getStats apiBaseUrl toMsg =
    Http.get
        { url = baseUrl apiBaseUrl ++ "/stats"
        , expect = Http.expectJson toMsg statsDecoder
        }

statsDecoder : Decode.Decoder Stats
statsDecoder =
    Decode.map6 Stats
        (Decode.field "total_orders" Decode.int)
        (Decode.field "grant_rate" Decode.float)
        (Decode.field "top_expert_type" (Decode.maybe Decode.string))
        (Decode.field "partial_count" Decode.int)
        (Decode.field "rulings" (Decode.dict Decode.int))
        (Decode.field "expert_types" (Decode.dict Decode.int))

-- GET /api/insights

getInsights : String -> (Result Http.Error (List Insight) -> msg) -> Cmd msg
getInsights apiBaseUrl toMsg =
    Http.get
        { url = baseUrl apiBaseUrl ++ "/insights"
        , expect = Http.expectJson toMsg (Decode.field "insights" (Decode.list insightDecoder))
        }

-- POST /api/search/keyword

keywordSearch : String -> String -> (Result Http.Error (List SearchResult) -> msg) -> Cmd msg
keywordSearch apiBaseUrl query toMsg =
    Http.post
        { url = baseUrl apiBaseUrl ++ "/search/keyword"
        , body = Http.jsonBody (Encode.object [ ( "query", Encode.string query ) ])
        , expect = Http.expectJson toMsg (Decode.list searchResultDecoder)
        }

-- POST /api/search/semantic

semanticSearch : String -> String -> (Result Http.Error (List SearchResult) -> msg) -> Cmd msg
semanticSearch apiBaseUrl query toMsg =
    Http.post
        { url = baseUrl apiBaseUrl ++ "/search/semantic"
        , body = Http.jsonBody (Encode.object [ ( "query", Encode.string query ) ])
        , expect = Http.expectJson toMsg (Decode.list searchResultDecoder)
        }

-- GET /api/orders/{id}

getOrderDetail : String -> Int -> (Result Http.Error OrderDetail -> msg) -> Cmd msg
getOrderDetail apiBaseUrl orderId toMsg =
    Http.get
        { url = baseUrl apiBaseUrl ++ "/orders/" ++ String.fromInt orderId
        , expect = Http.expectJson toMsg orderDetailDecoder
        }
```

---

## 6. Build & Deployment

### 6.1 Vite Configuration

**File:** `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import elmPlugin from 'vite-plugin-elm'

export default defineConfig({
  plugins: [elmPlugin()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 6.2 Package Configuration

**File:** `package.json`

```json
{
  "name": "know-your-judge-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vite": "^5.0.0",
    "vite-plugin-elm": "^3.0.0"
  }
}
```

**File:** `elm.json`

```json
{
    "type": "application",
    "source-directories": [
        "src"
    ],
    "elm-version": "0.19.1",
    "dependencies": {
        "direct": {
            "elm/browser": "1.0.2",
            "elm/core": "1.0.5",
            "elm/html": "1.0.0",
            "elm/http": "2.0.0",
            "elm/json": "1.1.3",
            "elm/url": "1.0.0"
        },
        "indirect": {
            "elm/bytes": "1.0.8",
            "elm/file": "1.0.5",
            "elm/time": "1.0.0",
            "elm/virtual-dom": "1.0.3"
        }
    },
    "test-dependencies": {
        "direct": {},
        "indirect": {}
    }
}
```

### 6.3 Development Workflow

```bash
# Install dependencies
npm install

# Start dev server (with backend proxy)
npm run dev
# Frontend: http://localhost:5173
# Backend: http://localhost:8000 (must be running)

# Build for production
npm run build
# Output: dist/
```

---

## 7. Performance Optimization

### 7.1 Code Splitting
Elm compiler automatically optimizes for minimal bundle size.

### 7.2 Lazy Loading
Load full order text only when detail page is visited.

### 7.3 Caching
Cache API responses in Model:
```elm
type alias Model =
    { cachedStats : Maybe Stats
    , cachedOrders : Dict Int OrderDetail
    }
```

### 7.4 Debouncing
Debounce search input:
```elm
-- Use ports to JavaScript setTimeout
port debounce : (String -> msg) -> Sub msg
```

---

## 8. Testing

```bash
# Install elm-test
npm install --save-dev elm-explorations/test

# Run tests
elm-test
```

**Sample test:**
```elm
module Tests.Api exposing (suite)

import Expect
import Test exposing (..)
import Api

suite : Test
suite =
    describe "API module"
        [ test "statsDecoder parses valid JSON" <|
            \_ ->
                let
                    json = """{"total_orders": 19, "grant_rate": 0.63}"""
                in
                Decode.decodeString Api.statsDecoder json
                    |> Expect.ok
        ]
```

---

## 9. Accessibility

- Semantic HTML (nav, main, article)
- ARIA labels for interactive elements
- Keyboard navigation (Tab, Enter, Esc)
- Focus indicators on all interactive elements
- Screen reader announcements for dynamic content

---

## 10. Success Metrics

- ✅ All pages load < 1 second
- ✅ Search results appear < 500ms
- ✅ Zero console errors
- ✅ Passes Lighthouse accessibility audit
- ✅ Works on mobile (responsive design)

---

**End of Frontend PRD**
