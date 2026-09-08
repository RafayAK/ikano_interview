function resolveSchema(propSchema, rootSchema) {
  if (propSchema.$ref) {
    const defName = propSchema.$ref.split("/").pop();
    return rootSchema.$defs?.[defName] ?? {};
  }
  if (propSchema.anyOf) {
    // Optional field, e.g. `X | None` — use the first non-null branch for widget type.
    return propSchema.anyOf.find((branch) => branch.type !== "null") ?? {};
  }
  return propSchema;
}

function fieldLabel(name, propSchema) {
  return propSchema.title || name.replace(/_/g, " ");
}

function createInputForProperty(name, propSchema, rootSchema, required, value = "") {
  const resolved = resolveSchema(propSchema, rootSchema);
  const wrapper = document.createElement("div");
  wrapper.className = "flex flex-col gap-1";

  if (resolved.type === "boolean") {
    wrapper.className = "flex items-center gap-2";
    const label = document.createElement("label");
    label.className = "flex items-center gap-2 text-sm text-slate-700";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = `field-${name}`;
    input.name = name;
    input.className = "h-4 w-4 rounded border-slate-300";
    input.checked = Boolean(value);
    label.append(input, document.createTextNode(fieldLabel(name, propSchema)));
    wrapper.append(label);
    return wrapper;
  }

  const label = document.createElement("label");
  label.className = "text-sm font-medium text-slate-700";
  label.textContent = fieldLabel(name, propSchema) + (required ? " *" : "");
  label.htmlFor = `field-${name}`;

  const input = document.createElement("input");
  input.id = `field-${name}`;
  input.name = name;
  input.required = required;
  input.className =
    "rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none";
  input.value = value ?? "";

  if (resolved.type === "integer") {
    input.type = "number";
    input.step = "1";
  } else if (resolved.type === "number") {
    input.type = "number";
    input.step = "any";
  } else {
    input.type = "text";
  }
  if (resolved.minimum !== undefined) input.min = resolved.minimum;
  if (resolved.exclusiveMinimum !== undefined) input.min = resolved.exclusiveMinimum;
  if (resolved.maximum !== undefined) input.max = resolved.maximum;

  wrapper.append(label, input);
  return wrapper;
}

function createArrayField(name, propSchema, rootSchema, required) {
  const itemSchema = resolveSchema(propSchema.items, rootSchema);
  const container = document.createElement("div");
  container.dataset.arrayField = name;
  container.className = "flex flex-col gap-3";

  const label = document.createElement("p");
  label.className = "text-sm font-medium text-slate-700";
  label.textContent = fieldLabel(name, propSchema) + (required ? " *" : "");
  container.append(label);

  const itemsHost = document.createElement("div");
  itemsHost.className = "flex flex-col gap-3";
  container.append(itemsHost);

  function addItem() {
    const itemWrapper = document.createElement("div");
    itemWrapper.className = "flex flex-col gap-2 rounded-md border border-slate-200 p-3";
    itemWrapper.dataset.arrayItem = "";

    for (const [subName, subSchema] of Object.entries(itemSchema.properties ?? {})) {
      const subRequired = (itemSchema.required ?? []).includes(subName);
      const field = createInputForProperty(subName, subSchema, rootSchema, subRequired);
      field.querySelector("input")?.setAttribute("data-sub-field", subName);
      itemWrapper.append(field);
    }

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Remove";
    removeButton.className = "self-start text-xs text-red-600 hover:underline";
    removeButton.addEventListener("click", () => itemWrapper.remove());
    itemWrapper.append(removeButton);

    itemsHost.append(itemWrapper);
  }

  const addButton = document.createElement("button");
  addButton.type = "button";
  addButton.textContent = `Add ${itemSchema.title ?? "item"}`;
  addButton.className =
    "self-start rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50";
  addButton.addEventListener("click", addItem);
  container.append(addButton);

  addItem(); // start with one row since most of these steps require at least one entry

  return container;
}

/** Renders a form into `container` from a Pydantic-generated JSON Schema. */
export function renderForm(container, schema) {
  container.innerHTML = "";
  const required = new Set(schema.required ?? []);

  if (!schema.properties || Object.keys(schema.properties).length === 0) {
    const note = document.createElement("p");
    note.className = "text-sm text-slate-500";
    note.textContent = "Nothing to fill in for this step — continue to run the check.";
    container.append(note);
    return;
  }

  for (const [name, propSchema] of Object.entries(schema.properties)) {
    const resolved = resolveSchema(propSchema, schema);
    const field =
      resolved.type === "array"
        ? createArrayField(name, propSchema, schema, required.has(name))
        : createInputForProperty(name, propSchema, schema, required.has(name));
    container.append(field);
  }
}

/** Reads the rendered form back into a plain object matching the schema's shape. */
export function collectFormAnswers(container, schema) {
  const answers = {};

  for (const [name, propSchema] of Object.entries(schema.properties ?? {})) {
    const resolved = resolveSchema(propSchema, schema);

    if (resolved.type === "array") {
      const arrayContainer = container.querySelector(`[data-array-field="${name}"]`);
      const itemSchema = resolveSchema(propSchema.items, schema);
      answers[name] = [...arrayContainer.querySelectorAll("[data-array-item]")].map((itemEl) => {
        const item = {};
        for (const subName of Object.keys(itemSchema.properties ?? {})) {
          const input = itemEl.querySelector(`[data-sub-field="${subName}"]`);
          item[subName] = coerceValue(input, itemSchema.properties[subName]);
        }
        return item;
      });
      continue;
    }

    const input = container.querySelector(`#field-${name}`);
    if (!input) continue;
    answers[name] = coerceValue(input, propSchema);
  }

  return answers;
}

function coerceValue(input, propSchema) {
  if (input.type === "checkbox") return input.checked;
  if (input.type === "number") {
    if (input.value === "") return null;
    return input.step === "1" ? parseInt(input.value, 10) : parseFloat(input.value);
  }
  return input.value;
}
