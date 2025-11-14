module Pages.Search exposing (Model, Msg(..), init, update, view)

import Api
import Components.SearchBar
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Http
import Types exposing (RemoteData(..), SearchResult, SearchType(..))


-- MODEL


type alias Model =
    { apiBaseUrl : String
    , query : String
    , searchType : SearchType
    , results : RemoteData Http.Error (List SearchResult)
    , hasSearched : Bool
    }


init : String -> String -> ( Model, Cmd Msg )
init apiBaseUrl initialQuery =
    let
        model =
            { apiBaseUrl = apiBaseUrl
            , query = initialQuery
            , searchType = Keyword
            , results = NotAsked
            , hasSearched = False
            }
    in
    if String.isEmpty initialQuery then
        ( model, Cmd.none )

    else
        ( { model | results = Loading, hasSearched = True }
        , performSearch apiBaseUrl Keyword initialQuery
        )


-- UPDATE


type Msg
    = QueryChanged String
    | SearchTypeChanged SearchType
    | SearchSubmitted
    | GotSearchResults (Result Http.Error (List SearchResult))
    | OrderSelected Int


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        QueryChanged query ->
            ( { model | query = query }, Cmd.none )

        SearchTypeChanged searchType ->
            ( { model | searchType = searchType }, Cmd.none )

        SearchSubmitted ->
            if String.isEmpty model.query then
                ( model, Cmd.none )

            else
                ( { model | results = Loading, hasSearched = True }
                , performSearch model.apiBaseUrl model.searchType model.query
                )

        GotSearchResults result ->
            case result of
                Ok results ->
                    ( { model | results = Success results }, Cmd.none )

                Err error ->
                    ( { model | results = Failure error }, Cmd.none )

        OrderSelected orderId ->
            -- Navigation will be handled by parent
            ( model, Cmd.none )


performSearch : String -> SearchType -> String -> Cmd Msg
performSearch apiBaseUrl searchType query =
    let
        params =
            { query = query
            , page = 0
            , limit = 20
            , minScore = Nothing  -- Use backend default (0.3)
            }
    in
    case searchType of
        Keyword ->
            Api.keywordSearch apiBaseUrl params GotSearchResults

        Semantic ->
            Api.semanticSearch apiBaseUrl params GotSearchResults


-- VIEW


view : Model -> (Msg -> msg) -> (Int -> msg) -> Html msg
view model toMsg onOrderSelect =
    div []
        [ div [ class "mb-8" ]
            [ h1 [ class "text-4xl font-bold text-blue-900 mb-2" ]
                [ text "Search Expert Orders" ]
            , p [ class "text-gray-600" ]
                [ text "Search Judge Boyle's expert witness rulings by methodology, Daubert standards, or expert qualifications" ]
            ]
        , Html.map toMsg (viewSearchBar model)
        , viewResults model toMsg onOrderSelect
        ]


viewSearchBar : Model -> Html Msg
viewSearchBar model =
    Components.SearchBar.view
        { query = model.query
        , searchType = model.searchType
        , onQueryChange = QueryChanged
        , onSearchTypeChange = SearchTypeChanged
        , onSubmit = SearchSubmitted
        , placeholder = "Search by Daubert, expert testimony, methodology, reliability..."
        }


viewResults : Model -> (Msg -> msg) -> (Int -> msg) -> Html msg
viewResults model toMsg onOrderSelect =
    case model.results of
        NotAsked ->
            if model.hasSearched then
                text ""

            else
                div [ class "text-center py-12" ]
                    [ div [ class "text-gray-400 text-6xl mb-4" ] [ text "?" ]
                    , p [ class "text-gray-600 text-lg" ]
                        [ text "Enter a search query to find relevant legal documents" ]
                    , p [ class "text-gray-500 text-sm mt-2" ]
                        [ text "Try searching for expert names, methodologies, or legal concepts" ]
                    ]

        Loading ->
            div [ class "py-8" ]
                [ div [ class "animate-pulse space-y-4" ]
                    [ div [ class "bg-gray-200 h-32 rounded-lg" ] []
                    , div [ class "bg-gray-200 h-32 rounded-lg" ] []
                    , div [ class "bg-gray-200 h-32 rounded-lg" ] []
                    ]
                ]

        Success results ->
            if List.isEmpty results then
                div [ class "text-center py-12 bg-gray-50 rounded-lg" ]
                    [ div [ class "text-gray-400 text-6xl mb-4" ] [ text "!" ]
                    , p [ class "text-gray-600 text-lg" ]
                        [ text "No results found" ]
                    , p [ class "text-gray-500 text-sm mt-2" ]
                        [ text "Try adjusting your search query or using different keywords" ]
                    ]

            else
                div []
                    [ div [ class "mb-4 text-sm text-gray-600" ]
                        [ text ("Found " ++ String.fromInt (List.length results) ++ " results") ]
                    , div [ class "space-y-4" ]
                        (List.map (viewResultCard onOrderSelect) results)
                    ]

        Failure error ->
            div [ class "bg-red-50 border border-red-200 rounded-lg p-6" ]
                [ p [ class "text-red-700 font-semibold mb-2" ]
                    [ text "Search failed" ]
                , p [ class "text-red-600" ]
                    [ text (Api.httpErrorToString error) ]
                ]


viewResultCard : (Int -> msg) -> SearchResult -> Html msg
viewResultCard onOrderSelect result =
    div
        [ class "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
        , onClick (onOrderSelect result.orderId)
        ]
        [ div [ class "flex items-start justify-between mb-3" ]
            [ h3 [ class "text-xl font-bold text-blue-900 flex-1" ]
                [ text result.caseName ]
            , span [ class "text-sm font-semibold text-blue-600 ml-4" ]
                [ text ("Score: " ++ String.fromFloat (result.score * 100) ++ "%") ]
            ]
        , div [ class "flex items-center gap-4 text-sm text-gray-600 mb-3" ]
            [ case result.metadata.date of
                Just date ->
                    span [] [ text date ]

                Nothing ->
                    text ""
            , if not (List.isEmpty result.metadata.expertNames) then
                span [] [ text (String.join ", " result.metadata.expertNames) ]

              else
                text ""
            , case result.metadata.rulingType of
                Just ruling ->
                    span [ class "px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium" ]
                        [ text ruling ]

                Nothing ->
                    text ""
            ]
        , p [ class "text-gray-700 mb-3" ]
            [ text result.snippet ]
        , case result.insights of
            Just insights ->
                if List.isEmpty insights then
                    text ""

                else
                    div [ class "flex flex-wrap gap-2" ]
                        (List.map viewInsightTag insights)

            Nothing ->
                text ""
        ]


viewInsightTag : String -> Html msg
viewInsightTag insight =
    span [ class "px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs" ]
        [ text insight ]
