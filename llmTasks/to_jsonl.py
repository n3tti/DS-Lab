import jsonlines


def to_jsonl(data, output_file):
    assert(output_file.endswith(".jsonl"))
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(data)