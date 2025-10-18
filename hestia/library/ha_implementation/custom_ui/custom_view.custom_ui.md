---
title: "Custom View Layout Development"
authors: "Home Assistant Developer Docs"
source: "developers.home-assistant.io"
slug: "custom-view-layout-development"
tags: ["home-assistant", "custom-ui", "view", "layout", "frontend"]
original_date: "2023-01-01"
last_updated: "2025-10-18"
url: "https://developers.home-assistant.io/docs/frontend/custom-ui/custom-view"
---

# Custom View Layout Development

## Table of Contents

- [Introduction](#introduction)
- [API Reference](#api-reference)
- [Example Implementation](#example-implementation)
- [Store Custom Data](#store-custom-data)
- [Edit, Delete, or Add a Card](#edit-delete-or-add-a-card)

## Introduction

By default Home Assistant will try to show the cards in a masonry layout (like Pinterest). A custom view layout allows developers to override this and define the layout mechanism (like a grid).

## API Reference
You define your custom view as a custom element. It's up to you to decide how to render your DOM inside your element. You can use Lit Element, Preact, or any other popular framework (except for React – more info on React here).

Custom Views receive the following:

```typescript
interface LovelaceViewElement {
  hass?: HomeAssistant;
  lovelace?: Lovelace;
  index?: number;
  cards?: Array<LovelaceCard | HuiErrorCard>;
  badges?: LovelaceBadge[];
  setConfig(config: LovelaceViewConfig): void;
}
```

Cards and Badges will be created and maintained by the core code and given to the custom view. The custom views are meant to load the cards and badges and display them in a customized layout.

## Example Implementation
(note: this example does not have all of the properties but the necessities to show the example)

```javascript
import { LitElement, html } from "https://unpkg.com/@polymer/lit-element@^0.6.1/lit-element.js?module";

class MyNewView extends LitElement {
  setConfig(_config) {}

  static get properties() {
    return {
      cards: {type: Array, attribute: false}
    };
  }

  render() {
    if(!this.cards) {
      return html``;
    }
    return html`${this.cards.map((card) => html`<div>${card}</div>`)}`;
  }
}
```

And you can define this element in the Custom Element Registry just as you would with a Custom Card:

```javascript
customElements.define("my-new-view", MyNewView);
```

A custom view can be used by adding the following to the definition of your view:

```yaml
- title: Home View
  type: custom:my-new-view
  badges: [...]
  cards: [...]
```

The default masonry view is an example of a layout element. (source).

## Store Custom Data
If your view requires data to persist at a card level, there is a view_layout in the card configuration that can be used to store information. Example: Key, X and Y coordinates, width and height, etc. This can be useful when you need to store the location or dimensions of a card for your view.

```yaml
- type: weather-card
  view_layout:
    key: 1234
    width: 54px
  entity: weather.my_weather
```

## Edit, Delete, or Add a Card
To call the core frontend dialogs to edit, delete or add a card, you can simply call these three events:

Event: "ll-delete-card"
Detail: { path: [number] | [number, number] }

Event: "ll-edit-card"
Detail: { path: [number] | [number, number] }

Event: "ll-create-card"
Detail: none
To call an event, you can use:

// Delete 4th card in the current view
this.dispatchEvent(new CustomEvent("ll-edit-card", { detail: { path: [3] } })) // this refers to the card element
Previous Chapter
Next Chapter
