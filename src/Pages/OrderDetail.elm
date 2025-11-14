module Pages.OrderDetail exposing (Model, Msg(..), init, update, view)

import Api
import Components.KeyCiteBadge
import Components.QuoteCard
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Http
import Types exposing (Citation, OrderDetail, Quote, RemoteData(..), Tab(..))


-- MODEL


type alias Model =
    { apiBaseUrl : String
    , orderId : Int
    , order : RemoteData Http.Error OrderDetail
    , activeTab : Tab
    , copiedQuoteId : Maybe String
    }


init : String -> Int -> ( Model, Cmd Msg )
init apiBaseUrl orderId =
    ( { apiBaseUrl = apiBaseUrl
      , orderId = orderId
      , order = Loading
      , activeTab = OverviewTab
      , copiedQuoteId = Nothing
      }
    , Api.getOrderDetail apiBaseUrl orderId GotOrderDetail
    )


-- UPDATE


type Msg
    = GotOrderDetail (Result Http.Error OrderDetail)
    | TabChanged Tab
    | CopyQuote String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotOrderDetail result ->
            case result of
                Ok order ->
                    ( { model | order = Success order }, Cmd.none )

                Err error ->
                    ( { model | order = Failure error }, Cmd.none )

        TabChanged tab ->
            ( { model | activeTab = tab }, Cmd.none )

        CopyQuote quoteText ->
            -- In a real app, would use ports to copy to clipboard
            ( { model | copiedQuoteId = Just quoteText }, Cmd.none )


-- VIEW


view : Model -> (Msg -> msg) -> Html msg
view model toMsg =
    case model.order of
        NotAsked ->
            text ""

        Loading ->
            div [ class "py-8" ]
                [ div [ class "animate-pulse" ]
                    [ div [ class "bg-gray-200 h-12 rounded-lg mb-4 w-2/3" ] []
                    , div [ class "bg-gray-200 h-8 rounded-lg mb-8 w-1/3" ] []
                    , div [ class "bg-gray-200 h-64 rounded-lg" ] []
                    ]
                ]

        Success order ->
            Html.map toMsg (viewOrder model order)

        Failure error ->
            div [ class "bg-red-50 border border-red-200 rounded-lg p-6" ]
                [ h2 [ class "text-xl font-bold text-red-700 mb-2" ]
                    [ text "Failed to load order details" ]
                , p [ class "text-red-600" ]
                    [ text (Api.httpErrorToString error) ]
                ]


viewOrder : Model -> OrderDetail -> Html Msg
viewOrder model order =
    div []
        [ viewHeader order
        , viewTabs model.activeTab
        , viewTabContent model order
        ]


viewHeader : OrderDetail -> Html msg
viewHeader order =
    div [ class "mb-8" ]
        [ h1 [ class "text-4xl font-bold text-blue-900 mb-4" ]
            [ text order.caseName ]
        , div [ class "flex flex-wrap gap-4 text-sm text-gray-600" ]
            [ case order.date of
                Just date ->
                    span [ class "flex items-center" ]
                        [ text ("Date: " ++ date) ]

                Nothing ->
                    text ""
            , case order.docketNumber of
                Just docket ->
                    span [ class "flex items-center" ]
                        [ text ("Docket: " ++ docket) ]

                Nothing ->
                    text ""
            , if not (List.isEmpty order.expertNames) then
                span [ class "flex items-center" ]
                    [ text ("Experts: " ++ String.join ", " order.expertNames) ]

              else
                text ""
            , span [ class "px-3 py-1 bg-blue-100 text-blue-700 rounded font-medium" ]
                [ text (String.fromInt order.wordCount ++ " words") ]
            , span [ class "px-3 py-1 bg-purple-100 text-purple-700 rounded font-medium" ]
                [ text (String.fromInt order.citationsCount ++ " citations") ]
            , if order.hasDaubertAnalysis then
                span [ class "px-3 py-1 bg-green-100 text-green-700 rounded font-medium" ]
                    [ text "Daubert Analysis" ]

              else
                text ""
            ]
        ]


viewTabs : Tab -> Html Msg
viewTabs activeTab =
    div [ class "border-b border-gray-200 mb-6" ]
        [ div [ class "flex space-x-8" ]
            [ viewTab activeTab OverviewTab "Overview"
            , viewTab activeTab AnalysisTab "Analysis"
            , viewTab activeTab FullTextTab "Full Text"
            , viewTab activeTab CitationsTab "Citations"
            , viewTab activeTab QuotesTab "Quotes"
            ]
        ]


viewTab : Tab -> Tab -> String -> Html Msg
viewTab activeTab tab label =
    let
        isActive =
            activeTab == tab

        classes =
            if isActive then
                "pb-4 px-1 border-b-2 border-blue-600 font-semibold text-blue-600 cursor-pointer"

            else
                "pb-4 px-1 border-b-2 border-transparent font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 cursor-pointer"
    in
    button
        [ class classes
        , onClick (TabChanged tab)
        ]
        [ text label ]


viewTabContent : Model -> OrderDetail -> Html Msg
viewTabContent model order =
    case model.activeTab of
        OverviewTab ->
            viewOverviewTab order

        AnalysisTab ->
            viewAnalysisTab order

        FullTextTab ->
            viewFullTextTab order

        CitationsTab ->
            viewCitationsTab order

        QuotesTab ->
            viewQuotesTab model order


viewOverviewTab : OrderDetail -> Html msg
viewOverviewTab order =
    div [ class "bg-white rounded-lg shadow-md p-6" ]
        [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
            [ text "Order Summary" ]
        , p [ class "text-gray-700 mb-6 leading-relaxed" ]
            [ text order.analysis.summary ]
        , div [ class "grid grid-cols-1 md:grid-cols-2 gap-6" ]
            [ viewInfoCard "Ruling Type" order.analysis.rulingType
            , viewInfoCard "Expert Field" order.analysis.expertField
            , div [ class "md:col-span-2" ]
                [ viewListCard "Methodologies" order.analysis.methodologies ]
            , div [ class "md:col-span-2" ]
                [ viewListCard "Exclusion Grounds" order.analysis.exclusionGrounds ]
            ]
        ]


viewInfoCard : String -> String -> Html msg
viewInfoCard title value =
    div [ class "bg-gray-50 rounded-lg p-4" ]
        [ p [ class "text-sm font-semibold text-gray-600 mb-1" ]
            [ text title ]
        , p [ class "text-lg text-gray-900" ]
            [ text value ]
        ]


viewListCard : String -> List String -> Html msg
viewListCard title items =
    div [ class "bg-gray-50 rounded-lg p-4" ]
        [ p [ class "text-sm font-semibold text-gray-600 mb-2" ]
            [ text title ]
        , if List.isEmpty items then
            p [ class "text-gray-500 italic" ] [ text "None specified" ]

          else
            ul [ class "list-disc list-inside space-y-1" ]
                (List.map (\item -> li [ class "text-gray-700" ] [ text item ]) items)
        ]


viewAnalysisTab : OrderDetail -> Html msg
viewAnalysisTab order =
    div [ class "space-y-6" ]
        [ div [ class "bg-white rounded-lg shadow-md p-6" ]
            [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                [ text "Key Findings" ]
            , if List.isEmpty order.analysis.keyFindings then
                p [ class "text-gray-500 italic" ] [ text "No key findings available" ]

              else
                ul [ class "space-y-3" ]
                    (List.map viewFinding order.analysis.keyFindings)
            ]
        , div [ class "bg-white rounded-lg shadow-md p-6" ]
            [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                [ text "Strategic Implications" ]
            , p [ class "text-gray-700 leading-relaxed" ]
                [ text order.analysis.strategicImplications ]
            ]
        , div [ class "bg-white rounded-lg shadow-md p-6" ]
            [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
                [ text "Citation Context" ]
            , p [ class "text-gray-700 leading-relaxed" ]
                [ text order.analysis.citationContext ]
            ]
        ]


viewFinding : String -> Html msg
viewFinding finding =
    li [ class "flex items-start" ]
        [ span [ class "text-blue-600 mr-2" ] [ text "-" ]
        , span [ class "text-gray-700" ] [ text finding ]
        ]


viewFullTextTab : OrderDetail -> Html msg
viewFullTextTab order =
    div [ class "bg-white rounded-lg shadow-md p-6" ]
        [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
            [ text "Full Document Text" ]
        , div [ class "prose max-w-none" ]
            [ pre [ class "whitespace-pre-wrap text-gray-700 font-mono text-sm leading-relaxed bg-gray-50 p-4 rounded" ]
                [ text order.fullText ]
            ]
        ]


viewCitationsTab : OrderDetail -> Html msg
viewCitationsTab order =
    div []
        [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
            [ text ("Citations (" ++ String.fromInt (List.length order.citations) ++ ")") ]
        , div [ class "bg-blue-50 border-l-4 border-blue-500 p-4 mb-6" ]
            [ div [ class "flex items-start" ]
                [ div [ class "flex-shrink-0" ]
                    [ span [ class "text-blue-600 text-xl mr-3" ] [ text "ℹ" ] ]
                , div []
                    [ p [ class "text-sm font-semibold text-blue-800 mb-1" ]
                        [ text "KeyCite Demo" ]
                    , p [ class "text-sm text-blue-700" ]
                        [ text "KeyCite status badges shown are demonstration data only. Real Westlaw KeyCite integration requires API access." ]
                    ]
                ]
            ]
        , if List.isEmpty order.citations then
            div [ class "bg-gray-50 rounded-lg p-8 text-center" ]
                [ p [ class "text-gray-500" ] [ text "No citations found" ] ]

          else
            div [ class "space-y-4" ]
                (List.map viewCitation order.citations)
        ]


viewCitation : Citation -> Html msg
viewCitation citation =
    div [ class "bg-white rounded-lg shadow-md p-6" ]
        [ div [ class "flex items-start justify-between mb-3" ]
            [ span [ class "text-sm font-semibold text-blue-600 uppercase" ]
                [ text citation.citationType ]
            ]
        , p [ class "text-gray-800 font-medium mb-3" ]
            [ text citation.text ]
        , case citation.keyCiteStatus of
            Just status ->
                div [ class "mb-3" ]
                    [ Components.KeyCiteBadge.view status ]

            Nothing ->
                text ""
        , case citation.context of
            Just context ->
                p [ class "text-sm text-gray-600 italic" ]
                    [ text context ]

            Nothing ->
                text ""
        ]


viewQuotesTab : Model -> OrderDetail -> Html Msg
viewQuotesTab model order =
    div []
        [ h2 [ class "text-2xl font-bold text-gray-800 mb-4" ]
            [ text ("Notable Quotes (" ++ String.fromInt (List.length order.quotes) ++ ")") ]
        , if List.isEmpty order.quotes then
            div [ class "bg-gray-50 rounded-lg p-8 text-center" ]
                [ p [ class "text-gray-500" ] [ text "No quotes available" ] ]

          else
            div [ class "space-y-4" ]
                (List.map (viewQuoteItem model) order.quotes)
        ]


viewQuoteItem : Model -> Quote -> Html Msg
viewQuoteItem model quote =
    Components.QuoteCard.view
        { quote = quote
        , onCopy = CopyQuote
        }
