module Components.StatCard exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)


type alias Config =
    { title : String
    , value : String
    , icon : String
    , color : String
    }


view : Config -> Html msg
view config =
    div [ class "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition" ]
        [ div [ class "flex items-center justify-between" ]
            [ div [ class "flex-1" ]
                [ p [ class "text-sm font-medium text-gray-600 mb-1" ]
                    [ text config.title ]
                , p [ class ("text-3xl font-bold " ++ config.color) ]
                    [ text config.value ]
                ]
            , div [ class ("text-4xl " ++ config.color) ]
                [ text config.icon ]
            ]
        ]
