# Labelled ground truth

Store human-labelled examples here.

Recommended layout:

```
data/labelled/
  121/
    dax_001.json
    dax_001.png
  caballo/
    dax_002.json
    dax_002.png
  negatives/
    not_121_001.json
    not_121_001.png
```

Each label should include the asset, timeframe, relevant timestamps/prices, direction, validity, notes and source image.

Positive examples alone are insufficient. Add ambiguous and negative examples too.
