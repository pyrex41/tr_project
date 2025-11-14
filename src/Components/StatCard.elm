module Components.StatCard exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)


type alias Config msg =
    { title : String
    , value : String
    , icon : String
    , color : String
    , onClick : Maybe msg
    }


view : Config msg -> Html msg
view config =
    let
        baseClasses =
            "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"

        clickableClasses =
            case config.onClick of
                Just _ ->
                    baseClasses ++ " cursor-pointer hover:bg-blue-50"

                Nothing ->
                    baseClasses

        attributes =
            case config.onClick of
                Just msg ->
                    [ class clickableClasses, onClick msg ]

                Nothing ->
                    [ class clickableClasses ]
    in
    div attributes
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
