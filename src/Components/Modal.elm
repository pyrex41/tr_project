module Components.Modal exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)


type alias Config msg =
    { isOpen : Bool
    , onClose : msg
    , title : String
    , content : List (Html msg)
    }


view : Config msg -> Html msg
view config =
    if config.isOpen then
        div [ class "fixed inset-0 z-50 overflow-y-auto" ]
            [ div [ class "flex items-center justify-center min-h-screen px-4" ]
                [ div
                    [ class "fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity"
                    , onClick config.onClose
                    ]
                    []
                , div [ class "relative bg-white rounded-lg shadow-xl max-w-3xl w-full z-10" ]
                    [ div [ class "flex items-center justify-between p-6 border-b border-gray-200" ]
                        [ h3 [ class "text-2xl font-bold text-gray-900" ]
                            [ text config.title ]
                        , button
                            [ class "text-gray-400 hover:text-gray-600 text-3xl leading-none"
                            , onClick config.onClose
                            ]
                            [ text "X" ]
                        ]
                    , div [ class "p-6" ]
                        config.content
                    ]
                ]
            ]

    else
        text ""
