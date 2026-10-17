# 0004. Native learner apps on iOS and Android

- Status: Proposed (to confirm by spike T162 in S6)
- Date: 2026-10-16

## Context

v1 ships a Next.js PWA. On iOS a wrapped website risks rejection under App Store guideline 4.2, and native features the product needs (Focus filters, Live Activities, widgets, Apple Pencil, VoiceOver quality) are only available natively.

## Decision (proposed)

Build native learner apps (SwiftUI on iOS, Kotlin with Compose on Android) that embed the existing simulation widget package through a bridge. Teacher, parent and school portals stay on the web.

## Consequences

Epic E16 adds 12 tickets and 78 points and two mobile engineers from S6 (superseded by ADR 0005: the Mobile agent role owns this work, no hires). Store compliance (Sign in with Apple, in-app account deletion, In-App Purchase, privacy declarations) is tracked in E16 and gates native go-live.
