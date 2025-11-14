module Api exposing
    ( getStats
    , getInsights
    , keywordSearch
    , semanticSearch
    , getOrderDetail
    , getOrders
    , httpErrorToString
    )

import Http
import Json.Decode as Decode
import Json.Encode as Encode
import Types exposing (..)


-- API BASE URL HELPER


buildUrl : String -> String -> String
buildUrl apiBaseUrl path =
    apiBaseUrl ++ path


-- GET STATS


getStats : String -> (Result Http.Error Stats -> msg) -> Cmd msg
getStats apiBaseUrl toMsg =
    Http.get
        { url = buildUrl apiBaseUrl "/api/stats"
        , expect = Http.expectJson toMsg statsDecoder
        }


-- GET INSIGHTS


getInsights : String -> (Result Http.Error (List Insight) -> msg) -> Cmd msg
getInsights apiBaseUrl toMsg =
    Http.get
        { url = buildUrl apiBaseUrl "/api/insights"
        , expect = Http.expectJson toMsg insightsListDecoder
        }


-- KEYWORD SEARCH


type alias KeywordSearchParams =
    { query : String
    , page : Int
    , limit : Int
    , minScore : Maybe Float  -- Optional minimum relevance threshold (0.0-1.0)
    }


keywordSearch : String -> KeywordSearchParams -> (Result Http.Error (List SearchResult) -> msg) -> Cmd msg
keywordSearch apiBaseUrl params toMsg =
    let
        baseParams =
            [ ( "query", Encode.string params.query )
            , ( "page", Encode.int params.page )
            , ( "limit", Encode.int params.limit )
            ]

        allParams =
            case params.minScore of
                Just score ->
                    baseParams ++ [ ( "min_score", Encode.float score ) ]

                Nothing ->
                    baseParams
    in
    Http.post
        { url = buildUrl apiBaseUrl "/api/search/keyword"
        , body = Http.jsonBody <| Encode.object allParams
        , expect = Http.expectJson toMsg searchResultsListDecoder
        }


-- SEMANTIC SEARCH


type alias SemanticSearchParams =
    { query : String
    , page : Int
    , limit : Int
    , minScore : Maybe Float  -- Optional minimum similarity threshold (0.0-1.0)
    }


semanticSearch : String -> SemanticSearchParams -> (Result Http.Error (List SearchResult) -> msg) -> Cmd msg
semanticSearch apiBaseUrl params toMsg =
    let
        baseParams =
            [ ( "query", Encode.string params.query )
            , ( "page", Encode.int params.page )
            , ( "limit", Encode.int params.limit )
            ]

        allParams =
            case params.minScore of
                Just score ->
                    baseParams ++ [ ( "min_score", Encode.float score ) ]

                Nothing ->
                    baseParams
    in
    Http.post
        { url = buildUrl apiBaseUrl "/api/search/semantic"
        , body = Http.jsonBody <| Encode.object allParams
        , expect = Http.expectJson toMsg searchResultsListDecoder
        }


-- GET ORDER DETAIL


getOrderDetail : String -> Int -> (Result Http.Error OrderDetail -> msg) -> Cmd msg
getOrderDetail apiBaseUrl orderId toMsg =
    Http.get
        { url = buildUrl apiBaseUrl ("/api/orders/" ++ String.fromInt orderId)
        , expect = Http.expectJson toMsg orderDetailDecoder
        }


-- GET ORDERS (PAGINATED LIST)


type alias GetOrdersParams =
    { page : Int
    , limit : Int
    }


getOrders : String -> GetOrdersParams -> (Result Http.Error (List OrderCard) -> msg) -> Cmd msg
getOrders apiBaseUrl params toMsg =
    let
        queryParams =
            "?page=" ++ String.fromInt params.page ++ "&limit=" ++ String.fromInt params.limit
    in
    Http.get
        { url = buildUrl apiBaseUrl ("/api/orders" ++ queryParams)
        , expect = Http.expectJson toMsg orderCardsListDecoder
        }


-- ERROR HANDLING HELPERS


httpErrorToString : Http.Error -> String
httpErrorToString error =
    case error of
        Http.BadUrl url ->
            "Invalid URL: " ++ url

        Http.Timeout ->
            "Request timed out"

        Http.NetworkError ->
            "Network error - please check your connection"

        Http.BadStatus status ->
            "Server error: " ++ String.fromInt status

        Http.BadBody message ->
            "Failed to parse response: " ++ message
