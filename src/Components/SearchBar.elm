module Components.SearchBar exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onInput, onClick)
import Types exposing (SearchType(..))


type alias Config msg =
    { query : String
    , searchType : SearchType
    , onQueryChange : String -> msg
    , onSearchTypeChange : SearchType -> msg
    , onSubmit : msg
    , placeholder : String
    }


view : Config msg -> Html msg
view config =
    div [ class "bg-white rounded-lg shadow-md p-6 mb-6" ]
        [ div [ class "flex flex-col md:flex-row gap-4" ]
            [ div [ class "flex-1" ]
                [ input
                    [ type_ "text"
                    , class "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    , placeholder config.placeholder
                    , value config.query
                    , onInput config.onQueryChange
                    ]
                    []
                ]
            , div [ class "flex gap-2" ]
                [ searchTypeButton config Keyword "Keyword"
                , searchTypeButton config Semantic "Semantic"
                ]
            , button
                [ class "px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                , onClick config.onSubmit
                ]
                [ text "Search" ]
            ]
        ]


searchTypeButton : Config msg -> SearchType -> String -> Html msg
searchTypeButton config searchType label =
    let
        isActive =
            config.searchType == searchType

        classes =
            if isActive then
                "px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg"

            else
                "px-4 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition"
    in
    button
        [ class classes
        , onClick (config.onSearchTypeChange searchType)
        ]
        [ text label ]
