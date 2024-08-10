function toggleSelection(element) {
  element.classList.toggle("selected");
  const checkbox = element.querySelector('input[type="checkbox"]');
  checkbox.checked = !checkbox.checked;
  if (checkbox.checked) {
    console.log("Selected tweak");
  } else {
    console.log("Unselected tweak");
  }
  var selectedTweaks = [];
  const tweakElements = document.querySelectorAll(".tweak.selected");
  tweakElements.forEach((tweak) => {
    const labelElement = tweak.querySelector(".tweak-info .tweak-title");
    selectedTweaks.push("**" + tweak.dataset.category);
    selectedTweaks.push(labelElement.textContent);
  });
  selectedTweaks = [...new Set(selectedTweaks)];
  document.getElementById("selected-tweaks").innerHTML = ""; // Clear the container
  selectedTweaks.forEach((tweak) => {
    const tweakItem = document.createElement("div");
    if (tweak.includes("**")) {
      // tweakItem.className = ("tweakListCategory")
      var label = document.createElement("label");
      tweak = tweak.substring(2);
      label.textContent = tweak;
      label.className = "tweak-list-category";
      tweakItem.append(label);
    } else {
      tweakItem.className = "tweak-list-pack";
      tweakItem.textContent = tweak;
    }
    document.getElementById("selected-tweaks").appendChild(tweakItem);
  });
  if (selectedTweaks.length == 0) {
    const tweakItem = document.createElement("div");
    tweakItem.className = "tweak-list-pack";
    tweakItem.textContent = "Select some packs and see them appear here!";
    document.getElementById("selected-tweaks").appendChild(tweakItem);
  }
}

window.addEventListener("resize", () => {
  if (window.matchMedia("(max-width: 767px)").matches) {
    document.getElementById("selected-tweaks").style.display = "none";
  } else {
    document.getElementById("selected-tweaks").style.display = "block";
  }
});

const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

function getTimeoutDuration() {
  return mediaQuery.matches ? 0 : 487.5;
}

function toggleCategory(label) {
  const tweaksContainer = label.nextElementSibling;
  const timeoutDuration = getTimeoutDuration();

  if (tweaksContainer.style.maxHeight) {
    tweaksContainer.style.maxHeight = null;
    setTimeout(() => {
      tweaksContainer.style.display = "none";
      tweaksContainer.style.paddingTop = null;
      tweaksContainer.style.paddingBottom = null;
      label.classList.toggle("open");
    }, timeoutDuration); // Matches the transition duration
  } else {
    tweaksContainer.style.display = "block";
    tweaksContainer.style.paddingTop = "7.5px";
    tweaksContainer.style.paddingBottom = "7.5px";
    label.classList.toggle("open");
    tweaksContainer.style.maxHeight = tweaksContainer.scrollHeight + "px";
    const outerCatLabel =
      label.parentElement.parentElement.previousElementSibling;
    const outerCatContainer = label.parentElement.parentElement;
    if (outerCatLabel.classList.contains("category-label")) {
      outerCatContainer.style.maxHeight =
        outerCatContainer.scrollHeight + tweaksContainer.scrollHeight + "px";
    }
  }
}

function downloadSelectedTweaks() {
  var mcVersion = document.getElementById("mev").value;
  console.log(`Minimum Engine Version is set to ${mcVersion}`);
  var packName = document.getElementById("fileNameInput").value;
  if (!packName) {
    packName = `BTCT-${String(Math.floor(Math.random() * 1000000)).padStart(6, "0")}`;
  }
  packName = packName.replaceAll("/", "-");
  const selectedTweaks = [];
  const tweakElements = document.querySelectorAll(".tweak.selected");
  tweakElements.forEach((tweak) => {
    selectedTweaks.push({
      category: tweak.dataset.category,
      name: tweak.dataset.name,
      index: parseInt(tweak.dataset.index),
    });
  });

  const tweaksByCategory = {
    Craftables: [],
    "More Blocks": [],
    "Quality of Life": [],
    Unpackables: [],
  };

  const indicesByCategory = {
    Craftables: [],
    "More Blocks": [],
    "Quality of Life": [],
    Unpackables: [],
  };

  selectedTweaks.forEach((tweak) => {
    tweaksByCategory[tweak.category].push(tweak.name);
    indicesByCategory[tweak.category].push(tweak.index);
  });

  const jsonData = {
    Craftables: {
      packs: tweaksByCategory["Craftables"],
      index: indicesByCategory["Craftables"],
    },
    "More Blocks": {
      packs: tweaksByCategory["More Blocks"],
      index: indicesByCategory["More Blocks"],
    },
    "Quality of Life": {
      packs: tweaksByCategory["Quality of Life"],
      index: indicesByCategory["Quality of Life"],
    },
    Unpackables: {
      packs: tweaksByCategory["Unpackables"],
      index: indicesByCategory["Unpackables"],
    },
    raw: selectedTweaks.map((tweak) => tweak.name),
  };

  fetchPack("https", jsonData, packName, mcVersion);
}
const serverip = "localhost";

function fetchPack(protocol, jsonData, packName, mcVersion) {
  console.log("Fetching pack...");
  fetch(`${protocol}://${serverip}/exportCraftingTweak`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      packName: packName,
      mcVersion: mcVersion,
    },
    body: JSON.stringify(jsonData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then((blob) => {
      console.log("Received pack!");
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `${packName}.mcpack`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch((error) => {
      if (protocol === "https") {
        console.error("HTTPS error, trying HTTP:", error);
        fetchPack("http", jsonData, packName, mcVersion); // Retry with HTTP
      } else {
        console.error("Error:", error);
      }
    });
}
