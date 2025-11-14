module Pages.Dashboard exposing (Model, Msg(..), init, update, view)

import Api
import Components.Chart
import Components.SearchBar
import Components.StatCard
import Dict
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Http
import Types exposing (ChartData, Insight, RemoteData(..), SearchType(..), Stats)


-- MODEL


type ModalType
    = OrdersModal
    | ExpertsModal
    | ExclusionModal
    | DaubertModal


type alias Model =
    { apiBaseUrl : String
    , stats : RemoteData Http.Error Stats
    , insights : RemoteData Http.Error (List Insight)
    , searchQuery : String
    , searchType : SearchType
    , modalState : Maybe ModalType
    , modalOrders : RemoteData Http.Error (List Types.OrderCard)
    }


init : String -> ( Model, Cmd Msg )
init apiBaseUrl =
    ( { apiBaseUrl = apiBaseUrl
      , stats = Loading
      , insights = Loading
      , searchQuery = ""
      , searchType = Keyword
      , modalState = Nothing
      , modalOrders = NotAsked
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
    | OpenModal ModalType
    | CloseModal
    | GotModalOrders (Result Http.Error (List Types.OrderCard))


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

        OpenModal modalType ->
            ( { model | modalState = Just modalType, modalOrders = Loading }
            , Api.getOrders model.apiBaseUrl { page = 0, limit = 100 } GotModalOrders
            )

        CloseModal ->
            ( { model | modalState = Nothing, modalOrders = NotAsked }, Cmd.none )

        GotModalOrders result ->
            case result of
                Ok orders ->
                    ( { model | modalOrders = Success orders }, Cmd.none )

                Err error ->
                    ( { model | modalOrders = Failure error }, Cmd.none )


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
        , Html.map toMsg (viewStats model)
        , viewInsights model
        , viewCharts model
        , Html.map toMsg (viewModal model)
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


viewStats : Model -> Html Msg
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
                        , onClick = Just (OpenModal OrdersModal)
                        }
                    , Components.StatCard.view
                        { title = "Total Experts"
                        , value = String.fromInt stats.totalExperts
                        , icon = "@"
                        , color = "text-green-600"
                        , onClick = Just (OpenModal ExpertsModal)
                        }
                    , Components.StatCard.view
                        { title = "Exclusion Rate"
                        , value = String.fromFloat stats.exclusionRate ++ "%"
                        , icon = "%"
                        , color = "text-red-600"
                        , onClick = Just (OpenModal ExclusionModal)
                        }
                    , Components.StatCard.view
                        { title = "Avg Citations"
                        , value = String.fromFloat stats.avgCitations
                        , icon = "*"
                        , color = "text-purple-600"
                        , onClick = Nothing
                        }
                    , Components.StatCard.view
                        { title = "Avg Word Count"
                        , value = String.fromInt stats.avgWordCount
                        , icon = "~"
                        , color = "text-orange-600"
                        , onClick = Nothing
                        }
                    , Components.StatCard.view
                        { title = "Daubert Analysis"
                        , value = String.fromInt stats.daubertAnalysisCount
                        , icon = "^"
                        , color = "text-indigo-600"
                        , onClick = Just (OpenModal DaubertModal)
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


-- MODAL VIEWS


viewModal : Model -> Html Msg
viewModal model =
    case model.modalState of
        Nothing ->
            text ""

        Just modalType ->
            div
                [ class "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
                , onClick CloseModal
                ]
                [ div [ class "bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden" ]
                    [ viewModalHeader modalType
                    , viewModalContent model modalType
                    ]
                ]


viewModalHeader : ModalType -> Html Msg
viewModalHeader modalType =
    div [ class "bg-blue-900 text-white px-6 py-4 flex items-center justify-between" ]
        [ h3 [ class "text-xl font-bold" ]
            [ text (modalTitle modalType) ]
        , button
            [ class "text-white hover:text-gray-200 text-2xl font-bold"
            , onClick CloseModal
            ]
            [ text "×" ]
        ]


modalTitle : ModalType -> String
modalTitle modalType =
    case modalType of
        OrdersModal ->
            "All Orders"

        ExpertsModal ->
            "All Experts"

        ExclusionModal ->
            "Exclusion Analysis"

        DaubertModal ->
            "Orders with Daubert Analysis"


viewModalContent : Model -> ModalType -> Html Msg
viewModalContent model modalType =
    div [ class "p-6 overflow-y-auto max-h-[calc(90vh-80px)]" ]
        [ case model.modalOrders of
            NotAsked ->
                text ""

            Loading ->
                div [ class "flex justify-center items-center py-12" ]
                    [ div [ class "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900" ] [] ]

            Failure error ->
                div [ class "bg-red-50 border border-red-200 rounded-lg p-4" ]
                    [ p [ class "text-red-700" ]
                        [ text "Failed to load data. Please try again." ]
                    ]

            Success orders ->
                case modalType of
                    OrdersModal ->
                        viewOrdersList orders

                    ExpertsModal ->
                        viewExpertsList orders

                    ExclusionModal ->
                        viewExclusionList orders

                    DaubertModal ->
                        viewDaubertList orders
        ]


viewOrdersList : List Types.OrderCard -> Html Msg
viewOrdersList orders =
    div [ class "space-y-4" ]
        (List.map viewOrderCard orders)


viewOrderCard : Types.OrderCard -> Html Msg
viewOrderCard order =
    div [ class "bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition" ]
        [ h4 [ class "text-lg font-bold text-blue-900 mb-2" ]
            [ text order.caseName ]
        , div [ class "flex items-center gap-4 text-sm text-gray-600 mb-2" ]
            [ case order.date of
                Just date ->
                    span [] [ text date ]

                Nothing ->
                    text ""
            , if not (List.isEmpty order.expertNames) then
                span [ class "text-gray-500" ]
                    [ text ("Experts: " ++ String.join ", " order.expertNames) ]

              else
                text ""
            ]
        , p [ class "text-gray-700 text-sm" ]
            [ text order.summary ]
        ]


viewExpertsList : List Types.OrderCard -> Html Msg
viewExpertsList orders =
    let
        -- Collect all unique experts with their cases
        expertsWithCases =
            orders
                |> List.concatMap (\order -> List.map (\expert -> ( expert, order )) order.expertNames)
                |> List.foldl
                    (\( expert, order ) acc ->
                        case Dict.get expert acc of
                            Just cases ->
                                Dict.insert expert (order :: cases) acc

                            Nothing ->
                                Dict.insert expert [ order ] acc
                    )
                    Dict.empty
                |> Dict.toList
    in
    div [ class "space-y-6" ]
        (List.map viewExpertGroup expertsWithCases)


viewExpertGroup : ( String, List Types.OrderCard ) -> Html Msg
viewExpertGroup ( expert, cases ) =
    div [ class "bg-gray-50 rounded-lg p-4" ]
        [ h4 [ class "text-lg font-bold text-green-700 mb-3" ]
            [ text expert
            , span [ class "text-sm text-gray-600 ml-2" ]
                [ text ("(" ++ String.fromInt (List.length cases) ++ " case" ++ (if List.length cases == 1 then "" else "s") ++ ")") ]
            ]
        , div [ class "space-y-2" ]
            (List.map viewExpertCase cases)
        ]


viewExpertCase : Types.OrderCard -> Html Msg
viewExpertCase order =
    div [ class "bg-white rounded p-3 text-sm" ]
        [ p [ class "font-semibold text-blue-900 mb-1" ]
            [ text order.caseName ]
        , p [ class "text-gray-700" ]
            [ text (String.left 150 order.summary ++ "...") ]
        ]


viewExclusionList : List Types.OrderCard -> Html Msg
viewExclusionList orders =
    div []
        [ p [ class "text-gray-600 mb-4" ]
            [ text "Analysis of expert exclusion patterns. Note: Detailed ruling information requires full order analysis." ]
        , viewOrdersList orders
        ]


viewDaubertList : List Types.OrderCard -> Html Msg
viewDaubertList orders =
    let
        -- Filter orders that likely have Daubert analysis (would need backend support for accurate filtering)
        daubertOrders =
            orders
                |> List.filter (\order -> String.contains "Daubert" order.summary || String.contains "daubert" order.summary)
    in
    if List.isEmpty daubertOrders then
        div [ class "text-center py-8" ]
            [ p [ class "text-gray-600" ]
                [ text "Daubert analysis information is available in full order details." ]
            , div [ class "mt-4" ]
                [ viewOrdersList orders ]
            ]

    else
        div []
            [ p [ class "text-gray-600 mb-4" ]
                [ text ("Showing " ++ String.fromInt (List.length daubertOrders) ++ " orders with Daubert analysis references") ]
            , viewOrdersList daubertOrders
            ]
