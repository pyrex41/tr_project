module Pages.Dashboard exposing (Model, Msg(..), init, update, view)

import Api
import Components.Chart
import Components.SearchBar
import Components.StatCard
import Html exposing (..)
import Html.Attributes exposing (..)
import Http
import Types exposing (ChartData, Insight, RemoteData(..), SearchType(..), Stats)


-- MODEL


type alias Model =
    { apiBaseUrl : String
    , stats : RemoteData Http.Error Stats
    , insights : RemoteData Http.Error (List Insight)
    , searchQuery : String
    , searchType : SearchType
    }


init : String -> ( Model, Cmd Msg )
init apiBaseUrl =
    ( { apiBaseUrl = apiBaseUrl
      , stats = Loading
      , insights = Loading
      , searchQuery = ""
      , searchType = Keyword
      }
    , Cmd.batch
        [ Api.getStats apiBaseUrl GotStats
        , Api.getInsights apiBaseUrl GotInsights
        ]
    )


-- UPDATE


type Msg
    = GotStats (Result Http.Error Stats)
    | GotInsights (Result Http.Error (List Insight))
    | SearchQueryChanged String
    | SearchTypeChanged SearchType
    | SearchSubmitted


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotStats result ->
            case result of
                Ok stats ->
                    ( { model | stats = Success stats }, Cmd.none )

                Err error ->
                    ( { model | stats = Failure error }, Cmd.none )

        GotInsights result ->
            case result of
                Ok insights ->
                    ( { model | insights = Success insights }, Cmd.none )

                Err error ->
                    ( { model | insights = Failure error }, Cmd.none )

        SearchQueryChanged query ->
            ( { model | searchQuery = query }, Cmd.none )

        SearchTypeChanged searchType ->
            ( { model | searchType = searchType }, Cmd.none )

        SearchSubmitted ->
            ( model, Cmd.none )


-- VIEW


view : Model -> (Msg -> msg) -> (String -> msg) -> Html msg
view model toMsg onNavigate =
    div []
        [ div [ class "mb-8" ]
            [ h1 [ class "text-4xl font-bold text-blue-900 mb-2" ]
                [ text "Judge Jane J. Boyle" ]
            , p [ class "text-xl text-gray-600" ]
                [ text "Expert Witness Ruling Patterns & Discovery Insights" ]
            , p [ class "text-sm text-gray-500 mt-2" ]
                [ text "U.S. District Court, Northern District of Texas - 19 Expert Orders Analyzed" ]
            ]
        , Html.map toMsg (viewSearchBar model)
        , viewStats model
        , viewInsights model
        , viewCharts model
        ]


viewSearchBar : Model -> Html Msg
viewSearchBar model =
    Components.SearchBar.view
        { query = model.searchQuery
        , searchType = model.searchType
        , onQueryChange = SearchQueryChanged
        , onSearchTypeChange = SearchTypeChanged
        , onSubmit = SearchSubmitted
        , placeholder = "Quick search: Daubert standards, expert qualifications, methodology..."
        }


viewStats : Model -> Html msg
viewStats model =
    case model.stats of
        NotAsked ->
            text ""

        Loading ->
            div [ class "mb-8" ]
                [ div [ class "animate-pulse" ]
                    [ div [ class "grid grid-cols-1 md:grid-cols-3 gap-6" ]
                        [ div [ class "bg-gray-200 h-32 rounded-lg" ] []
                        , div [ class "bg-gray-200 h-32 rounded-lg" ] []
                        , div [ class "bg-gray-200 h-32 rounded-lg" ] []
                        ]
                    ]
                ]

        Success stats ->
            div [ class "mb-8" ]
                [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                    [ text "Key Statistics" ]
                , div [ class "grid grid-cols-1 md:grid-cols-3 gap-6" ]
                    [ Components.StatCard.view
                        { title = "Total Orders"
                        , value = String.fromInt stats.totalOrders
                        , icon = "#"
                        , color = "text-blue-600"
                        }
                    , Components.StatCard.view
                        { title = "Total Experts"
                        , value = String.fromInt stats.totalExperts
                        , icon = "@"
                        , color = "text-green-600"
                        }
                    , Components.StatCard.view
                        { title = "Exclusion Rate"
                        , value = String.fromFloat stats.exclusionRate ++ "%"
                        , icon = "%"
                        , color = "text-red-600"
                        }
                    , Components.StatCard.view
                        { title = "Avg Citations"
                        , value = String.fromFloat stats.avgCitations
                        , icon = "*"
                        , color = "text-purple-600"
                        }
                    , Components.StatCard.view
                        { title = "Avg Word Count"
                        , value = String.fromInt stats.avgWordCount
                        , icon = "~"
                        , color = "text-orange-600"
                        }
                    , Components.StatCard.view
                        { title = "Daubert Analysis"
                        , value = String.fromInt stats.daubertAnalysisCount
                        , icon = "^"
                        , color = "text-indigo-600"
                        }
                    ]
                ]

        Failure _ ->
            div [ class "mb-8 bg-red-50 border border-red-200 rounded-lg p-4" ]
                [ p [ class "text-red-700" ]
                    [ text "Failed to load statistics. Please try refreshing the page." ]
                ]


viewInsights : Model -> Html msg
viewInsights model =
    case model.insights of
        NotAsked ->
            text ""

        Loading ->
            div [ class "mb-8" ]
                [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                    [ text "AI-Discovered Insights" ]
                , div [ class "animate-pulse" ]
                    [ div [ class "bg-gray-200 h-24 rounded-lg mb-3" ] []
                    , div [ class "bg-gray-200 h-24 rounded-lg mb-3" ] []
                    ]
                ]

        Success insights ->
            if List.isEmpty insights then
                text ""

            else
                div [ class "mb-8" ]
                    [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                        [ text "AI-Discovered Insights" ]
                    , div [ class "grid grid-cols-1 md:grid-cols-2 gap-4" ]
                        (List.map viewInsightCard insights)
                    ]

        Failure _ ->
            div [ class "mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4" ]
                [ p [ class "text-yellow-700" ]
                    [ text "Failed to load insights." ]
                ]


viewInsightCard : Insight -> Html msg
viewInsightCard insight =
    div [ class "bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500" ]
        [ div [ class "flex items-center justify-between mb-2" ]
            [ span [ class "text-xs font-semibold text-blue-600 uppercase" ]
                [ text insight.insightType ]
            , span [ class "text-xs text-gray-500" ]
                [ text (String.fromFloat (insight.confidence * 100) ++ "% confidence") ]
            ]
        , p [ class "text-gray-800 mb-2" ]
            [ text insight.description ]
        , div [ class "text-sm text-gray-600" ]
            [ text ("Evidence: " ++ String.fromInt (List.length insight.evidence) ++ " orders") ]
        ]


viewCharts : Model -> Html msg
viewCharts model =
    case model.stats of
        Success stats ->
            div [ class "mb-8" ]
                [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                    [ text "Visual Analytics" ]
                , div [ class "grid grid-cols-1 md:grid-cols-2 gap-6" ]
                    [ div [ class "bg-white rounded-lg shadow-md p-6" ]
                        [ h3 [ class "text-lg font-semibold text-gray-700 mb-4" ]
                            [ text "Orders Distribution" ]
                        , Components.Chart.barChart
                            [ { label = "Total", value = toFloat stats.totalOrders, color = "#2563eb" }
                            , { label = "With Daubert", value = toFloat stats.daubertAnalysisCount, color = "#7c3aed" }
                            , { label = "Experts", value = toFloat stats.totalExperts, color = "#059669" }
                            ]
                        ]
                    , div [ class "bg-white rounded-lg shadow-md p-6" ]
                        [ h3 [ class "text-lg font-semibold text-gray-700 mb-4" ]
                            [ text "Metrics Overview" ]
                        , Components.Chart.pieChart
                            [ { label = "Avg Citations", value = stats.avgCitations, color = "#8b5cf6" }
                            , { label = "Avg Words", value = toFloat stats.avgWordCount / 100, color = "#f97316" }
                            , { label = "Exclusion %", value = stats.exclusionRate, color = "#ef4444" }
                            ]
                        ]
                    ]
                ]

        _ ->
            text ""
