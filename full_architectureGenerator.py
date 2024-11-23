import oyaml as yaml
import os
from itertools import product

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Get all variants of one component
def get_variants(component_name, component_config):
    for component in component_config['components']:
        if component['name'] == component_name:
            return [variant['name'] for variant in component['variants']]
    return []

# Get allowed hosts for a specific component and variant
def get_allowed_hosts(variant_name, component_config):
    for component in component_config['components']:
        for variant in component['variants']:
            if variant['name'] == variant_name:
                return variant.get('allowed_hosts', [])
    return []

# Check if a combination of source and target component is allowed in componentConfig.yaml
def is_combination_valid(source_component, target_component, component_config):
    allowed_hosts = get_allowed_hosts(source_component, component_config)
    valid = False
    if target_component in allowed_hosts:
        valid = True
    # elif allowed_hosts[0] == "all OS":
    #     if target_component in get_variants('OS', component_config):
    #         valid = True
    elif allowed_hosts[0] == "all":
        valid = True

    return valid

# Generate all combinations of each stack tier with all of the related component variants
def generate_component_combinations(stack_config, component_config):
    component_combinations = {}

    for stack in stack_config['stacks']:
        for tier in stack['tiers']:
            tier_name = tier['name']
            component_combinations[tier_name] = []

            # Get all variants for each component in the current tier
            component_variants = [get_variants(component['type'], component_config) for component in tier['components']]
            # Combine all variants of the components
            tier_combinations = product(*component_variants)

            for combination in tier_combinations:
                valid_combination = True
                # Check the allowed hosts for each component in the combination
                for i in range(len(combination)-1):
                    if not is_combination_valid(combination[i], combination[i+1], component_config):
                        valid_combination = False
                        break
                
                if valid_combination:
                    component_combinations[tier_name].append(combination)
    
    return component_combinations

def all_components_from_same_provider(combination):
    providers = ['Amazon', 'Azure', 'Google']
    counts = {provider: 0 for provider in providers}
    for stack in combination:
        for component in stack:
            for provider in providers:
                if provider in component:
                    counts[provider] += 1
                    break
                

    num_valid_providers = sum(1 for count in counts.values() if count > 0)

    return num_valid_providers <= 1

def generate_full_architectures(component_combinations, base_architectures_path, full_architecture_path):

    for filename in os.listdir(base_architectures_path):
        if filename.endswith(".yaml"):  # Only process YAML files
            file_path = os.path.join(base_architectures_path, filename)
            print(f"Processing file: {file_path}")

            # Load the current YAML file
            base_architecture = load_yaml(file_path)
            #for stack in base_architecture['stacks']:

            # List to store tier names present in the current architecture
            tiers_in_architecture = []

            # Get all tiers from the base architecture
            for stack in base_architecture['architecture'][0]['stacks']:
                tier_name = stack['name']
                tiers_in_architecture.append(tier_name)

            # Get all possible variants for the tiers in the current architecture
            tier_variants = [component_combinations[tier_name] for tier_name in tiers_in_architecture if tier_name in component_combinations]

            # Combine the variants of different tiers to form full architectures
            full_combinations = product(*tier_variants)

            # Iterate over all combinations and generate full architectures

            combination_counter = 0

            for combination in full_combinations:

                # Check if only one provider is present in combination --> to allow only architectures with IaaS or aaS solutions from one provider
                if not all_components_from_same_provider(combination):
                    continue

                combination_counter += 1
                new_architecture = {
                    'architecture': [		   
                        {
                            'name': base_architecture['architecture'][0]['name'],  # Keep the original name
                            'stacks': [],
                            'relationships': base_architecture['architecture'][0]['relationships']  # Keep relationships between stacks
                        }
                    ]
                }

                # For each tier, add the selected variant combination
                for i, stack in enumerate(base_architecture['architecture'][0]['stacks']):
                    tier_name = stack['tier']
                    variant_combination = combination[i]

                    new_components = []
                    for component, variant in zip(stack['components'], variant_combination):
                        new_components.append({
                            'type': component['type'], # Keep the original component type
                            'variant': variant,
                            'id': component['id']  # Keep the original component ID
                        })

                    new_stack = {
                        'tier': tier_name, # Keep the original tier
                        'name': stack['name'], # Keep the original stack name
                        'components': new_components,
                        'relationships': stack.get('relationships', [])  # Keep existing relationships in the stack
                    }
                    new_architecture['architecture'][0]['stacks'].append(new_stack)

                # Save the new architecture with combined variants
                filename_without_extension = os.path.splitext(filename)[0]
                output_filename = f"{filename_without_extension}-{combination_counter}.yaml"
                output_file_path = os.path.join(full_architecture_path, output_filename)

                comment = "# architecture style: ASYaml"


                # # Write the new architecture to a YAML file
                # with open(output_file_path, 'w') as full_file:
                #     yaml.dump(new_architecture, full_file, default_flow_style=False)

                # Write the new architecture to a YAML file
                with open(output_file_path, 'w') as full_file:
                    # Write the comment manually before dumping the YAML
                    full_file.write(comment + "\n")  # Write the comment first
                    yaml.dump(new_architecture, full_file, default_flow_style=False)

def main():
    stack_config = load_yaml('Config/stackConfig.yaml')
    component_config = load_yaml('Config/componentConfig.yaml')
    base_architectures_path = 'generatedFiles/base'
    full_architecture_path = 'generatedFiles/full'

    component_combinations = generate_component_combinations(stack_config, component_config)

    generate_full_architectures(component_combinations, base_architectures_path, full_architecture_path)

if __name__ == '__main__':
    main()
