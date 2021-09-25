import pandas as pd


def test(data, context):
    save_path = 'gs://strengths-finder-app/test.csv'
    list1 = ["a1", "a2", "a3"]
    df = pd.DataFrame(list1)
    df.to_csv(save_path)
    print("Job finished.")
