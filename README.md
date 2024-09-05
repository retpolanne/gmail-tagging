# GMail tagging

## Flattening the resulting json and getting the top domains

Based on [1]

```sh
jq  '. | to_entries | sort_by(.value.message_ids|length) | reverse | map({key: .key, value: .value.message_ids | length}) | from_entries' res.json
```

## References

[1] https://github.com/jbranchaud/til/blob/master/jq/count-each-collection-in-a-json-object.md
