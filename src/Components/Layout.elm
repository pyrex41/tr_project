module Components.Layout exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)


type alias Config msg =
    { currentPage : String
    , onNavigate : String -> msg
    }


view : Config msg -> List (Html msg) -> Html msg
view config content =
    div [ class "min-h-screen bg-gray-50" ]
        [ header [ class "bg-blue-900 text-white shadow-lg" ]
            [ div [ class "container mx-auto px-4 py-4" ]
                [ div [ class "flex items-center justify-between" ]
                    [ h1 [ class "text-2xl font-bold" ]
                        [ text "Legal Document Analysis" ]
                    , nav [ class "flex space-x-6" ]
                        [ navLink config "Dashboard" "/"
                        , navLink config "Search" "/search"
                        ]
                    ]
                ]
            ]
        , main_ [ class "container mx-auto px-4 py-8" ]
            content
        , footer [ class "bg-gray-800 text-white mt-12" ]
            [ div [ class "container mx-auto px-4 py-6 text-center" ]
                [ p [ class "text-sm" ]
                    [ text "Legal Document Analysis System - 2025" ]
                ]
            ]
        ]


navLink : Config msg -> String -> String -> Html msg
navLink config label path =
    let
        isActive =
            config.currentPage == path

        activeClasses =
            if isActive then
                "border-b-2 border-white font-semibold"

            else
                "hover:border-b-2 hover:border-blue-300"
    in
    a
        [ class ("pb-1 cursor-pointer " ++ activeClasses)
        , onClick (config.onNavigate path)
        ]
        [ text label ]
