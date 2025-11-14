module Components.KeyCiteBadge exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Types exposing (KeyCiteStatus)


view : KeyCiteStatus -> Html msg
view status =
    let
        ( badgeColor, textColor, flagIcon ) =
            case status.flag of
                "red" ->
                    ( "bg-red-100 border-red-500", "text-red-800", "⚠" )

                "yellow" ->
                    ( "bg-yellow-100 border-yellow-500", "text-yellow-800", "⚡" )

                "blue" ->
                    ( "bg-blue-100 border-blue-500", "text-blue-800", "ℹ" )

                "green" ->
                    ( "bg-green-100 border-green-500", "text-green-800", "✓" )

                _ ->
                    ( "bg-gray-100 border-gray-500", "text-gray-800", "?" )

        treatmentText =
            case status.treatment of
                "overruled" ->
                    "Overruled"

                "questioned" ->
                    "Questioned"

                "distinguished" ->
                    "Distinguished"

                "good_law" ->
                    "Good Law"

                _ ->
                    status.treatment
    in
    div [ class "inline-flex items-center gap-2 px-3 py-1 rounded-md border-2", class badgeColor, class textColor ]
        [ span [ class "text-lg font-bold" ] [ text flagIcon ]
        , div [ class "flex flex-col" ]
            [ span [ class "text-xs font-semibold" ] [ text treatmentText ]
            , span [ class "text-xs opacity-75" ]
                [ text (String.fromInt status.citingCases ++ " citing cases") ]
            ]
        , a
            [ href "#"
            , class "text-xs underline ml-2"
            , title "View on Westlaw (Demo)"
            ]
            [ text "Westlaw" ]
        ]
