module Components.QuoteCard exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Types exposing (Quote)


type alias Config msg =
    { quote : Quote
    , onCopy : String -> msg
    }


view : Config msg -> Html msg
view config =
    div [ class "bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-600 mb-4" ]
        [ div [ class "flex justify-between items-start mb-3" ]
            [ h4 [ class "text-sm font-semibold text-gray-600 uppercase" ]
                [ text config.quote.relevance ]
            , button
                [ class "px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded hover:bg-blue-200 transition"
                , onClick (config.onCopy config.quote.text)
                , title "Copy quote"
                ]
                [ text "Copy" ]
            ]
        , blockquote [ class "text-gray-800 italic mb-3 text-lg" ]
            [ text ("\"" ++ config.quote.text ++ "\"") ]
        , p [ class "text-sm text-gray-600" ]
            [ span [ class "font-semibold" ] [ text "Context: " ]
            , text config.quote.context
            ]
        ]
