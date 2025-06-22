import argparse
from pathlib import Path


def generate_label_studio_config(topics):
    """
    Build a Label Studio XML config by combining:
     1) a static header (all of your <Style> + Excerpt block)
     2) a loop that emits one <Text> + <Choices> block per topic
     3) a static footer (closing tags for </View>)
    """
    static_header = """<View>
    <Style>
      .box {
        font-family: "Times New Roman", serif !important;
        background: #FDF6E3;
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
      }
      .container {
        flex: 50%;
        padding: 20px;
        max-width: 900px;
      }
      .excerpt {
        max-width: 700px;
        min-width: 600px;
      }
      .stances {
        position: sticky;
        top: 16px;

        max-width: 700px;
        min-width: 600px;
        
        align-self: flex-start;
      }
      .text * {
        font-family: "Times New Roman", serif !important;
        font-size: 20px;
        line-height: 2;
        text-align: justify;
      }
      .box h4.ant-typography {
        font-size: 24px;
      }

      .stance-header-row {
        display: flex;
      }
      .stance-header-row .topic-header {
        flex: 1;
        font-weight: bold;
      }
      .stance-header-row .options-header {
        flex: 2;
        display: flex;
        justify-content: space-around;
        font-weight: bold;
      }

      .stance-row {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
      }
      .stance-label {
        flex: 1;
        font-size: 16px;
        padding-right: 10px;
      }
      .stance-options .ant-checkbox-wrapper {
        margin: 0 !important;
      }
      .lsf-choices {
        margin: 0 !important;
      }
    </Style>

    <View className="box">
      <View className="container excerpt">
        <Header value="Excerpt"></Header>
        <View className="text">
          <Text name="text" value="$text" />
        </View>
      </View>
      <View className="container stances">
        <Header value="Stances"/>
    """

    static_footer = """
      </View>
    </View>
</View>"""

    # Build the dynamic portion in one go:
    dynamic_blocks = []
    for idx, topic in enumerate(topics, start=1):
        dynamic_blocks.append(f'        <View className="stance-row">')
        dynamic_blocks.append(f'          <View className="stance-label">')
        dynamic_blocks.append(f'            <Text name="stance-{idx}" value="{idx}. {topic}"/>')
        dynamic_blocks.append(f'          </View>')
        dynamic_blocks.append(f'          <View className="stance-options">')
        dynamic_blocks.append(f'            <Choices name="stance-on-topic-{idx}" toName="text" choice="single" showInLine="true">')
        dynamic_blocks.append(f'              <Choice value="Negative"/>')
        dynamic_blocks.append(f'              <Choice value="Neutral" selected="true"/>')
        dynamic_blocks.append(f'              <Choice value="Positive"/>')
        dynamic_blocks.append(f'            </Choices>')
        dynamic_blocks.append(f'          </View>')
        dynamic_blocks.append(f'        </View>')

    # Join everything with newlines
    return "\n".join([static_header] + dynamic_blocks + [static_footer])


def parse_txt_to_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Create Labelling Template for Label Studio")
    
    parser.add_argument('folder')
    parser.add_argument('-t', '--topics', default="topics.txt")
    parser.add_argument('-o', '--output', default="template")

    args = parser.parse_args()

    hearing = args.folder
    path = f"hearings/{hearing}"
    topics = args.topics
    output = f"{args.output}.xml"

    list_of_topics = parse_txt_to_list(f"{path}/{topics}")
    xml_config = generate_label_studio_config(list_of_topics)
    Path(f"{path}/{output}").write_text(xml_config, "utf-8")

    print(f"✓ Created XML labelling template for Label Studio ({path}/{output})")

    n = 30

    print("-" * n, "XML Template", "-" * n)
    print(xml_config)
    print("-" * (n * 2 + 12 + 2))
