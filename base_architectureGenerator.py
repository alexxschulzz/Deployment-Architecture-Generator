# oyaml is an extensions of the yaml lib = ordered yaml, ensures that the order of the e.g. dict in python is preserved in the created yaml file
import oyaml as yaml
from itertools import product
import os
import re
import uuid
import shutil

# architecture file directory
base_architectures_path = 'Files/File_Generator/generatedFiles/base'

# config files
stack_config_path = 'Files/File_Generator/Config/stackConfig.yaml'
combination_config_path = 'Files/File_Generator/Config/stackCombinationConfig.yaml'

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_basestack_architecture(architecture, architecture_counter):
    os.makedirs(base_architectures_path, exist_ok=True)

    output_file_path = os.path.join(base_architectures_path, f'CloudArchitecture{architecture_counter}.yaml')

    # avoids, that yaml dumper is using aliases/referencing in the created yaml file but instead creates an own structure for e.g. WebApp and WebApp-2
    yaml.Dumper.ignore_aliases = lambda *args : True
    with open(output_file_path, 'w') as file:
        yaml.dump(architecture, file, default_flow_style=False)

def strip_number_from_stack_name(stack_name):
    return re.sub(r'-\d+$', '', stack_name)

def get_stack_top_component_id(stack_structure):
    return stack_structure['components'][0]['id'] if stack_structure['components'] else None

def generate_stack_combinations(stack_config, combination_config):
    architecture_counter = 1

    for combination in combination_config['combinations']:
        stacks = combination['stacks']
        relationships = combination['relationships']

        # This functionality is needed when there are e.g. two WebApps: WebApp and WebApp-2.
        # It ensures that the tier WebApp is added 2 times to stack_tiers even though it has the same tier
        stack_tiers = {}
        for stack in stacks:
            stack_name = strip_number_from_stack_name(stack)
            for default_stack in stack_config['stacks']:
                default_stack_name = default_stack['stack']
                if stack_name == default_stack_name:
                    stack_tiers[stack] = default_stack['tiers']
                    break
        
        print("++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"Processing new combination: {combination['name']}")
        print("Default architecture consists of following stacks and tiers:")
        for stack_name, tiers in stack_tiers.items():
            print(f"{stack_name}: {[tier_info['name'] for tier_info in tiers]}")
        print("----------")
        
        # All stack tiers present in the stack combination are combined with each other in all possible combinations
        print("Combine all stack tiers with each other...")
        tier_combinations = product(*[tiers for tiers in stack_tiers.values()])

        # Go through all stack tiers combinations and create an architecture file for it
        for tier_combination in tier_combinations:
            print("----------")
            print("Create architecture:")
            architecture_name = f"CloudArchitecture{architecture_counter}"
            architecture = {
                'architecture': [{
                    'name': architecture_name,
                    'stacks': [],
                    'relationships': []
                }]
            }

            # add the stacks for this combination
            for stack_name, stack_info in zip(stacks, tier_combination):
                # Keep the original name so that a distinction can be made between two stacks of the same tier.
                original_stack_name = stack_name

                print(f"Checking stack: {stack_name}, tier: {stack_info['name']}")
                try:
                    stack_details = next(stack for stack in stack_tiers[stack_name] if stack['name'] == stack_info['name'])
                except StopIteration:
                    print(f"Error: No stack found for {stack_name} with tier {stack_info['name']}.")
                    continue
                
                stack_structure = {
                    'tier': original_stack_name,
                    'name': stack_info['name'],
                    'components': [],
                    'relationships': list(stack_details['relationships'])
                }

                # Add components with generated short UUID
                for component in stack_details['components']:
                    component_id = str(str(uuid.uuid4())[:13])  # generate short UUID
                    component_structure = {
                        'type': component['type'],
                        'id': component_id
                    }
                    stack_structure['components'].append(component_structure)

                # Update relationships to use component_id instead of type
                updated_relationships = []
                for relationship in stack_structure['relationships']:
                    source_id = next((comp['id'] for comp in stack_structure['components'] if comp['type'] == relationship['source']), relationship['source'])
                    target_id = next((comp['id'] for comp in stack_structure['components'] if comp['type'] == relationship['target']), relationship['target'])
                    
                    updated_relationships.append({
                        'source': source_id,
                        'target': target_id,
                        'type': relationship['type']
                    })

                # Replace the original relationships with the id based ones
                stack_structure['relationships'] = updated_relationships

                # Append the updated stack structure to the architecture
                architecture['architecture'][0]['stacks'].append(stack_structure)

            # Add relationships between the stacks
            for relationship in relationships:
                # identify source and target stack
                source_stack_structure = next(
                    (stack for stack in architecture['architecture'][0]['stacks'] if stack['tier'] == relationship['source']),
                    None
                )
                target_stack_structure = next(
                    (stack for stack in architecture['architecture'][0]['stacks'] if stack['tier'] == relationship['target']),
                    None
                )

                source_id = get_stack_top_component_id(source_stack_structure)
                target_id = get_stack_top_component_id(target_stack_structure)

                # Add the ID of the top component of each stack
                architecture['architecture'][0]['relationships'].append({
                    'source': source_id,
                    'target': target_id,
                    'relationship': relationship['relationship']
                })

            # Save the architecture in a .yaml file
            save_basestack_architecture(architecture, architecture_counter)
            print(f"Architecture {architecture_name} saved.")
            architecture_counter += 1

def main():
    stack_config = load_yaml(stack_config_path)
    combination_config = load_yaml(combination_config_path)

    # delete files in output_directory/base_architectures_path before new generation
    if os.path.exists(base_architectures_path):
        # deleting the entire folder is faster
        shutil.rmtree(base_architectures_path)
        print ()
        print(f"Delete existing files in '{base_architectures_path}' before generating the base architectures...")
        print()
        # recreate the folder
        os.makedirs(base_architectures_path)

    generate_stack_combinations(stack_config, combination_config)

if __name__ == "__main__":
    main()
