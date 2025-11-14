module Types exposing (..)

import Json.Decode as Decode exposing (Decoder, field, int, string, float, list, bool, nullable)
import Json.Decode.Pipeline exposing (required, optional)


-- REMOTE DATA


type RemoteData e a
    = NotAsked
    | Loading
    | Success a
    | Failure e


-- SEARCH TYPES


type SearchType
    = Keyword
    | Semantic


-- TAB TYPES


type Tab
    = OverviewTab
    | AnalysisTab
    | FullTextTab
    | CitationsTab
    | QuotesTab


-- STATS


type alias Stats =
    { totalOrders : Int
    , totalExperts : Int
    , exclusionRate : Float
    , avgCitations : Float
    , avgWordCount : Int
    , daubertAnalysisCount : Int
    }


statsDecoder : Decoder Stats
statsDecoder =
    Decode.succeed Stats
        |> required "total_orders" int
        |> required "total_experts" int
        |> required "exclusion_rate" float
        |> required "avg_citations" float
        |> required "avg_word_count" int
        |> required "daubert_analysis_count" int


-- INSIGHT


type alias Insight =
    { id : String
    , insightType : String
    , description : String
    , evidence : List Int
    , confidence : Float
    , strength : String
    }


insightDecoder : Decoder Insight
insightDecoder =
    Decode.succeed Insight
        |> required "id" string
        |> required "type" string
        |> required "description" string
        |> required "evidence" (list int)
        |> required "confidence" float
        |> required "strength" string


insightsListDecoder : Decoder (List Insight)
insightsListDecoder =
    list insightDecoder


-- SEARCH RESULT


type alias SearchResult =
    { orderId : Int
    , caseName : String
    , snippet : String
    , score : Float
    , insights : Maybe (List String)
    , metadata : ResultMetadata
    }


type alias ResultMetadata =
    { date : Maybe String
    , expertNames : List String
    , rulingType : Maybe String
    }


searchResultDecoder : Decoder SearchResult
searchResultDecoder =
    Decode.succeed SearchResult
        |> required "order_id" int
        |> required "case_name" string
        |> required "snippet" string
        |> required "score" float
        |> optional "insights" (nullable (list string)) Nothing
        |> required "metadata" resultMetadataDecoder


resultMetadataDecoder : Decoder ResultMetadata
resultMetadataDecoder =
    Decode.succeed ResultMetadata
        |> optional "date" (nullable string) Nothing
        |> required "expert_names" (list string)
        |> optional "ruling_type" (nullable string) Nothing


searchResultsListDecoder : Decoder (List SearchResult)
searchResultsListDecoder =
    list searchResultDecoder


-- ORDER DETAIL


type alias OrderDetail =
    { id : Int
    , caseName : String
    , date : Maybe String
    , docketNumber : Maybe String
    , expertNames : List String
    , fullText : String
    , citationsCount : Int
    , wordCount : Int
    , hasDaubertAnalysis : Bool
    , analysis : OrderAnalysis
    , citations : List Citation
    , quotes : List Quote
    }


type alias OrderAnalysis =
    { summary : String
    , rulingType : String
    , expertField : String
    , methodologies : List String
    , exclusionGrounds : List String
    , keyFindings : List String
    , strategicImplications : String
    , citationContext : String
    }


type alias Citation =
    { text : String
    , citationType : String
    , context : Maybe String
    , keyCiteStatus : Maybe KeyCiteStatus
    }


type alias KeyCiteStatus =
    { flag : String  -- "red", "yellow", "blue", "green"
    , treatment : String  -- "overruled", "questioned", "distinguished", "good_law"
    , citingCases : Int
    }


type alias Quote =
    { id : String
    , text : String
    , context : String
    , relevance : String
    }


orderDetailDecoder : Decoder OrderDetail
orderDetailDecoder =
    Decode.succeed OrderDetail
        |> required "id" int
        |> required "case_name" string
        |> optional "date" (nullable string) Nothing
        |> optional "docket_number" (nullable string) Nothing
        |> required "expert_names" (list string)
        |> required "full_text" string
        |> required "citations_count" int
        |> required "word_count" int
        |> required "has_daubert_analysis" bool
        |> required "analysis" orderAnalysisDecoder
        |> required "citations" (list citationDecoder)
        |> required "quotes" (list quoteDecoder)


orderAnalysisDecoder : Decoder OrderAnalysis
orderAnalysisDecoder =
    Decode.succeed OrderAnalysis
        |> required "summary" string
        |> required "ruling_type" string
        |> required "expert_field" string
        |> required "methodologies" (list string)
        |> required "exclusion_grounds" (list string)
        |> required "key_findings" (list string)
        |> required "strategic_implications" string
        |> required "citation_context" string


citationDecoder : Decoder Citation
citationDecoder =
    Decode.succeed Citation
        |> required "text" string
        |> required "type" string
        |> optional "context" (nullable string) Nothing
        |> optional "keycite_status" (nullable keyCiteStatusDecoder) Nothing


keyCiteStatusDecoder : Decoder KeyCiteStatus
keyCiteStatusDecoder =
    Decode.succeed KeyCiteStatus
        |> required "flag" string
        |> required "treatment" string
        |> required "citing_cases" int


quoteDecoder : Decoder Quote
quoteDecoder =
    Decode.succeed Quote
        |> required "id" string
        |> required "text" string
        |> required "context" string
        |> required "relevance" string


-- ORDER CARD (for lists)


type alias OrderCard =
    { id : Int
    , caseName : String
    , date : Maybe String
    , expertNames : List String
    , summary : String
    , hasDaubertAnalysis : Bool
    , hasExclusion : Bool
    }


orderCardDecoder : Decoder OrderCard
orderCardDecoder =
    Decode.succeed OrderCard
        |> required "id" int
        |> required "case_name" string
        |> optional "date" (nullable string) Nothing
        |> required "expert_names" (list string)
        |> required "summary" string
        |> required "has_daubert_analysis" bool
        |> optional "has_exclusion" bool False


orderCardsListDecoder : Decoder (List OrderCard)
orderCardsListDecoder =
    list orderCardDecoder


-- CHART DATA


type alias ChartData =
    { label : String
    , value : Float
    , color : String
    }


chartDataDecoder : Decoder ChartData
chartDataDecoder =
    Decode.succeed ChartData
        |> required "label" string
        |> required "value" float
        |> required "color" string
